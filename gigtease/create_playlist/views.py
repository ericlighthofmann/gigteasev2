from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import spotipy
import spotipy.util as util
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.exceptions import SuspiciousOperation


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
