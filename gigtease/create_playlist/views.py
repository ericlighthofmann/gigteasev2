import json
from datetime import datetime

import requests
from celery.result import allow_join_result
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Playlist
from .tasks import query_seatgeek_api, create_spotify_playlist


def create_playlist(request):
    # config
    default_miles = 30

    if settings.DEBUG:
        redirect_uri = 'http://127.0.0.1:8000/create-playlist'
    else:
        redirect_uri = 'https://gigtease.com/create-playlist'
    session_id = str(request.COOKIES.get('sessionid'))

    spotify_authorize_url = (
        'https://accounts.spotify.com/authorize?' +
        'client_id=e0ac4d1f574f4242b6b7163f08dcaffe' +
        '&redirect_uri=' + redirect_uri +
        '&scope=playlist-modify-public' +
        '&response_type=code' +
        '&state=' + session_id +
        '&show_dialog=true'
    )

    return render(request, 'pages/create-playlist.html', {
        'default_miles': default_miles,
        'redirect_uri': redirect_uri,
        'spotify_authorize_url': spotify_authorize_url,
    })


@csrf_exempt
def get_access_token_spotify(request):
    if settings.DEBUG:
        redirect_uri = 'http://127.0.0.1:8000/create-playlist'
    else:
        redirect_uri = 'https://gigtease.com/create-playlist'
    if request.method == "POST":
        base_url = 'https://accounts.spotify.com/api/token'
        data = {
            'grant_type': 'authorization_code',
            'code': request.POST.get('code'),
            'redirect_uri': redirect_uri,
            'client_id': 'e0ac4d1f574f4242b6b7163f08dcaffe',
            'client_secret': '273590643fef46329d40d478cbd1d4ea'
        }
        spotify_response = requests.post(base_url, data=data)
        if spotify_response.ok:
            spotify_response = spotify_response.json()
            return JsonResponse(spotify_response)
        else:
            return HttpResponseBadRequest('Bad request.')
    else:
        raise SuspiciousOperation('Invalid request - needs to come from a POST.')


@csrf_exempt
def write_payload_and_task_id_to_db(request):
    if request.method == "POST":
        location_zip = request.POST.get('locationZip')
        location_name = request.POST.get('locationName')
        genres = ','.join(request.POST.getlist('genres[]'))
        start_date = datetime.strptime(request.POST.get('startDate'), '%m/%d/%Y')
        end_date = datetime.strptime(request.POST.get('endDate'), '%m/%d/%Y')
        distance = request.POST.get('distance')
        task_id = request.POST.get('task_id')
        auth_token = request.POST.get('auth_token')
        Playlist.objects.update_or_create(
            task_id=task_id,
            defaults={
                'location_zip': location_zip,
                'location_name': location_name,
                'genres': genres,
                'start_date': start_date,
                'end_date': end_date,
                'distance': distance,
                'auth_token': auth_token,
            }
        )
        return HttpResponse('success')
    else:
        raise SuspiciousOperation('Invalid request - needs to come from a POST.')


@csrf_exempt
def create_playlist_in_progress(request, task_id):
    payload = Playlist.objects.filter(
        task_id=task_id
    ).values()
    task_status = query_seatgeek_api.AsyncResult(task_id+'_seatgeek').status
    print ('seatgeek_task_status: ', str(task_status))
    if task_status != 'SUCCESS':
        query_seatgeek_api.apply_async(
            kwargs={
                'location_zip': payload[0]['location_zip'],
                'location_name': payload[0]['location_name'],
                'genres': payload[0]['genres'],
                'start_date': payload[0]['start_date'],
                'end_date': payload[0]['end_date'],
                'distance': payload[0]['distance'],
                'auth_token': payload[0]['auth_token']
            },
            task_id=task_id+'_seatgeek',
        )
    payload = json.dumps(list(payload), default=str)
    return render(request, 'pages/create-playlist-in-progress.html', {
        'task_id': task_id,
        'payload': payload,
    })


@csrf_exempt
def get_seatgeek_query_results(request, task_id):
    result = query_seatgeek_api.AsyncResult(task_id+'_seatgeek')
    with allow_join_result():
        return JsonResponse({
            'all_performers': len(list(result.get()['all_performers'])),
            'event_info': result.get()['event_info'],
            'location_zip': result.get()['location_zip'],
            'location_name': result.get()['location_name'],
            'genres': result.get()['genres'],
            'start_date': result.get()['start_date'],
            'end_date': result.get()['end_date'],
            'distance': result.get()['distance'],
            'task_id': result.task_id,
        })


@csrf_exempt
def kick_off_spotify(request, seatgeek_task_id):
    seatgeek_result = query_seatgeek_api.AsyncResult(seatgeek_task_id+'_seatgeek')
    with allow_join_result():
        all_bands_seatgeek = seatgeek_result.get()['all_performers']

        all_event_info = seatgeek_result.get()['event_info']
        # get unique bands between the two lists
        all_bands = all_bands_seatgeek
        auth_token = seatgeek_result.get()['auth_token']
        location_name = seatgeek_result.get()['location_name']
        start_date = seatgeek_result.get()['start_date']
        end_date = seatgeek_result.get()['end_date']
        create_spotify_playlist.apply_async(
            kwargs={
                'auth_token': auth_token,
                'all_bands': all_bands,
                'start_date': start_date,
                'end_date': end_date,
                'location_name': location_name,
                'all_event_info': all_event_info
            },
            task_id=seatgeek_task_id+'_spotify',
        )
        return JsonResponse({
            'total_bands': str(len(all_bands)),
            'task_id': seatgeek_task_id,
        })

@csrf_exempt
def get_spotify_playlist_results(request, task_id):
    result = create_spotify_playlist.AsyncResult(task_id+'_spotify')
    with allow_join_result():
        spotify_playlist_link = result.get()['created_playlist_url']
        concert_info_link = '/dashboard/' + task_id
        return JsonResponse({
            'spotify_playlist_link': spotify_playlist_link,
            'concert_info_link': concert_info_link,
        })
