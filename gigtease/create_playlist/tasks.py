import time
from datetime import datetime
from dateutil import parser

import requests
import spotipy
from celery import shared_task
from celery.utils.log import get_task_logger
from celery_progress.backend import ProgressRecorder
from django.utils import dateformat
from spotipy.oauth2 import SpotifyClientCredentials

logger = get_task_logger(__name__)

# run celery with celery -A config.celery_app worker --loglevel=INFO -P solo

@shared_task(bind=True)
def query_seatgeek_api(self, location_zip, location_name, genres, start_date, end_date, distance, auth_token):
    progress_recorder = ProgressRecorder(self)

    # configure user inputs for api call
    distance = str(distance) + 'mi'
    # api key
    client_id = 'MTY5MTMzMjB8MTU1OTc4OTQxNi40Ng'

    api_call_data = [
        'geoip=' + str(location_zip) + '&range=' + distance,
        'per_page=5000',
        'datetime_local.gt=' + start_date,
        'datetime_local.lt=' + end_date,
        'genres.slug=' + genres,
        #'listing_count.gt=0',
        'taxonomies.name=concert'
    ]

    # this is our base call function
    base_url = 'https://api.seatgeek.com/2/events?client_id=' + client_id
    def api_call(modifiers):
        modified_url = base_url
        for modifier in modifiers:
            modified_url += '&' + modifier
        return requests.get(modified_url).json()

    # just getting the first page...5000 results should be enough
    # and every other page has an empty events array anyway
    events = api_call(api_call_data)
    all_performers = []
    event_info = []
    for key, val in events.items():
        if key == 'events':
            for event_idx, event in enumerate(val):
                # add artificial sleep to make the progress bar look cooler...
                time.sleep(.01)
                progress_recorder.set_progress(event_idx+1, len(val))
                ticket_url = event['url']
                date = event['datetime_local']
                venue_name = event['venue']['name']
                try:
                    venue_address = event['venue']['address'] + ' ' + event['venue']['extended_address']
                except TypeError:
                    venue_address = ''
                performers = event['performers']
                for performer_idx, performer in enumerate(performers):
                    current_performer = performer['name']
                    if current_performer not in all_performers:
                        all_performers.append(current_performer)
                        current_event = {}
                        current_event['artist_name'] = current_performer
                        current_event['ticket_url'] = ticket_url
                        current_event['date'] = date
                        current_event['venue_name'] = venue_name
                        current_event['venue_address'] = venue_address
                        event_info.append(current_event)
    return {
        'event_info': event_info,
        'all_performers': all_performers, 'auth_token': auth_token,
        'location_zip': location_zip, 'location_name': location_name, 'genres': genres,
        'start_date': start_date, 'end_date': end_date, 'distance': distance,
    }


@shared_task(bind=True)
def create_spotify_playlist(self, auth_token, all_bands, start_date, end_date, location_name, all_event_info):
    progress_recorder = ProgressRecorder(self)
    playlist_tracks = []
    spotify_client_id = 'e0ac4d1f574f4242b6b7163f08dcaffe'
    spotify_client_secret = '273590643fef46329d40d478cbd1d4ea'
    client_credentials_manager = SpotifyClientCredentials(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
    )
    spotify = spotipy.Spotify(auth=auth_token)
    spotify_username = spotify.me()['id']

    logger.info('getting artists most popular tracks...')
    # only allowing 100 artists (spotify playlist limit)
    all_bands = list(set(all_bands[:100]))
    band_song_dict = {}
    for i, artist in enumerate(all_bands):
        logger.info(artist)
        progress_recorder.set_progress(i, len(all_bands))
        top_tracks_list = []
        # search by artist name to get the artist uri
        results = spotify.search(q='artist:' + artist, type='artist')
        try:
            artist_uri = results['artists']['items'][0]['uri']
        except IndexError:
            continue
        top_tracks = spotify.artist_top_tracks(artist_uri)
        for track, values in top_tracks.items():
            try:
                # artist_top_tracks orders by popularity by default
                track_uri = values[0]['uri']
                track_name = values[0]['name']
                all_event_info_obj = [x for x in all_event_info if x['artist_name'] == artist][0]
                date = datetime.strftime(
                    datetime.strptime(all_event_info_obj['date'].split('T')[0], '%Y-%m-%d'),
                    '%m/%d/%Y'
                )
                venue_name = all_event_info_obj['venue_name']
                venue_address = all_event_info_obj['venue_address']
                seatgeek_ticket_url = all_event_info_obj['ticket_url']
                ticketmaster_ticket_url = all_event_info_obj['ticket_url']
                band_song_dict[artist] = {
                    'track_name': track_name,
                    'embed_code': 'https://open.spotify.com/embed/track/'+track_uri.split('spotify:track:')[1],
                    'date': date,
                    'venue_name': venue_name,
                    'venue_address': venue_address,
                    'seatgeek_ticket_url': seatgeek_ticket_url,
                    'ticketmaster_ticket_url': ticketmaster_ticket_url,
                }
                playlist_tracks.append(track_uri)
            except IndexError:
                continue

    # create playlist based off of all tracks collected
    logger.info('creating playlist...')
    if playlist_tracks:
        # TODO parser.parse is super slow - should just send over a date object in the correct string, not times
        start_time = dateformat.format(
            parser.parse(start_date), 'M jS Y'
        )
        end_time = dateformat.format(
            parser.parse(end_date), 'M jS Y'
        )
        playlist_name = ('GigTease - bands coming to ' + location_name +
            ' between ' + start_time + ' and ' + end_time
        )

        created_playlist = spotify.user_playlist_create(spotify_username, playlist_name, public=True)
        created_playlist_id = created_playlist['id']
        created_playlist_url = created_playlist['external_urls']['spotify']
        # can add 100 tracks at once
        if playlist_tracks:
            spotify.user_playlist_add_tracks(spotify_username, created_playlist_id, playlist_tracks)
    else:
        created_playlist_url = ''

    return {
        'band_song_dict': band_song_dict,
        'created_playlist_url': created_playlist_url,
    }
