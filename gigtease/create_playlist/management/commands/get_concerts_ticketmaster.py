import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime
from tqdm import tqdm
import time
import json
import pprint
import re

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Uses the Ticket Master API to get concerts for each location.'

    def handle(self, *args, **options):

        #progress_recorder = ProgressRecorder(self)

        # DEFINE FAKE USER INPUTS
        time_period = 2
        distance = '15'
        location_name = 'San Diego'
        genres = ['Rock', 'Alternative']

        # configure user inputs for api call
        date_modifier = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S') + ',' + datetime.strftime(
            datetime.now() + relativedelta(weeks=int(time_period))
        , '%Y-%m-%d')+'T23:59:59'
        distance = str(distance.replace('mi', ''))

        api_call_data = [
            'city=' + location_name,
            'locale=*',
            'radius=' + distance,
            'unit=miles',
            'localStartEndDateTime=' + date_modifier,
            'size=200',
            #'page=1',
        ]
        #api_call_data.append(
        #    'genres.slug=' + ','.join(genres)
        #)

        # this is our base call function
        base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?'
        client_id = 'vQtUwod3pGmdb6217kSvoOsI5A7E2KEi'
        def api_call(modifiers):
            modified_url = base_url
            for modifier in modifiers:
                modified_url += '&' + modifier
            modified_url = modified_url + '&apikey=' + client_id
            return requests.get(modified_url).json()

        events = api_call(api_call_data)
        try:
            events_base = events['_embedded']['events']
        except KeyError:
            pass

        all_performers = []
        for i, event in enumerate(events_base):
            #progress_recorder.set_progress(i, len(events_base))
            # adding to make progress bars look cooler
            time.sleep(.02)
            classification_name = event['classifications'][0]['segment']['name']
            if classification_name != 'Music':
                continue
            print (json.dumps(event, indent=4))
            assert False
            date = event['dates']['start']['localDate']
            for key, val in event.items():
                if type(val) == dict:
                    venue_name = val['venues'][0]['name']
                    venue_city = val['venues'][0]['city']['name']
                    vevnue_state = val['venues'][0]['state']['stateCode']
                    venue_zip = val['venues'][0]['postalCode']
                    venue_address = val['venues'][0]['address']['line1'] + \
                        ' ' + venue_city + ', ' + venue_state + ' ' + venue_zip
                    ticket_url = val['attractions']['url']
                    date = ''
                    # TODO get all this data (ticket_url, venue info, etc)
                    # and pass through to Spotify, do it in tasks.py
                    for k, v in val.items():
                        if k == 'attractions':
                            for e in v:
                                try:
                                    artist_name = e['name']
                                    genre = e['classifications'][0]['genre']['name']
                                    if genre in genres or genres == ['']:
                                        all_performers.append(artist_name)
                                except KeyError:
                                    continue
        print('Found ' + str(len(all_performers)) + ' performers from Ticketmaster!')
