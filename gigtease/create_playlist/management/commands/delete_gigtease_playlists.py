from django.core.management.base import BaseCommand

import os
from tqdm import tqdm
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class Command(BaseCommand):
    def handle(self, *args, **options):
        os.environ["SPOTIPY_CLIENT_ID"] = 'e0ac4d1f574f4242b6b7163f08dcaffe'
        os.environ["SPOTIPY_CLIENT_SECRET"] = '273590643fef46329d40d478cbd1d4ea'

        scope = "playlist-modify-public"
        spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=scope,
            redirect_uri='http://127.0.0.1:8000/create-playlist-in-progress'
        ))

        playlists = spotify.current_user_playlists()
        for key, val in playlists.items():
            if key == 'items':
                for v in tqdm(val):
                    if v['name'].startswith('GigTease'):
                        spotify.current_user_unfollow_playlist(v['id'])


