from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import spotipy
import spotipy.util as util
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.exceptions import SuspiciousOperation
from .tasks import query_seatgeek_api


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
def create_playlist_in_progress(request, task_id):
    return render(request, 'pages/create-playlist-in-progress.html', {
        'task_id': task_id
    })


@csrf_exempt
def kick_off_seatgeek_api_query(request):
    if request.method == "POST":
        location_zip = request.POST.get('locationZip', '')
        location_name = request.POST.get('locationName', '')
        genres = request.POST.getlist('genres[]', '')
        start_date = request.POST.get('startDate', '')
        end_date = request.POST.get('endDate', '')
        distance = request.POST.get('distance', '')
        auth_token = request.POST.get('auth_token', '')
        result = query_seatgeek_api.delay(location_zip, location_name, genres, start_date, end_date, distance,
                                          auth_token)
        return HttpResponse(result.task_id)
    else:
        raise SuspiciousOperation('Invalid request - needs to come from a POST.')
