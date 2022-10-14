import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime
from tqdm import tqdm
import time
import json
import pprint
import re
from config.settings.base import TICKETMASTER_CLIENT_ID

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Uses the Ticket Master API to get concerts for each location.'

    def handle(self, *args, **options):

        # progress_recorder = ProgressRecorder(self)

        # DEFINE FAKE USER INPUTS
        time_period = 2
        distance = '15'
        location_name = 'Seattle'
        zip_code = '92116'
        genres = ['Rock', 'Alternative']

        # configure user inputs for api call
        date_modifier = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S') + ',' + datetime.strftime(
            datetime.now() + relativedelta(weeks=int(time_period))
            , '%Y-%m-%d') + 'T23:59:59'
        distance = str(distance.replace('mi', ''))

        api_call_data = [
            'city=' + location_name,
            # 'postalCode=' + zip_code,
            'locale=*',
            'radius=' + distance,
            'unit=miles',
            'localStartEndDateTime=' + date_modifier,
            'size=200',
            # 'page=1',
        ]
        api_call_data.append(
            'genres.slug=' + ','.join(genres)
        )

        # this is our base call function
        base_url = 'https://app.ticketmaster.com/discovery/v2/events.json?'

        def api_call(modifiers):
            modified_url = base_url
            for modifier in modifiers:
                modified_url += '&' + modifier
            modified_url = modified_url + '&apikey=' + TICKETMASTER_CLIENT_ID
            return requests.get(modified_url).json()

        events = api_call(api_call_data)

        # writing to json object, just for viewing and debug
        json_object = json.dumps(events, indent=4)
        with open("gigtease/ticketmaster_result.json", "w") as outfile:
            outfile.write(json_object)

        # this is where the actual data starts
        events_base = events['_embedded']['events']

        all_performers = []
        error_count = 0
        results_dict = {}
        for i, event in enumerate(events_base):
            classification_name = event['classifications'][0]['segment']['name']
            if classification_name != 'Music':
                continue

            # the artist and ticket url seems to be in two different places...
            # one is _embedded and one is in the base event
            try:
                artist_name = event['_embedded']['attractions'][0]['name']
            except KeyError:
                try:
                    artist_name = event['name']
                except KeyError:
                    error_count += 1
                    continue

            try:
                ticket_url = event['_embedded']['attractions'][0]['url']
            except KeyError:
                try:
                    ticket_url = event['url'].split('www.ticketmaster.com')[1].replace('%2F', '')
                except (KeyError, IndexError):
                    print (artist_name)
                    error_count += 1
                    continue


            date = event['dates']['start']['localDate']
            venues = event['_embedded']['venues'][0]
            venue_name = venues['name']
            venue_city = venues['city']['name']
            venue_state = venues['state']['name']
            venue_zip = venues['postalCode']
            venue_address = venues['address']['line1'] + ' ' + venue_city + ',' + venue_state + ' ' + venue_zip

            all_performers.append(artist_name)

            results_dict[artist_name] = {
                'date': date,
                'venue_name': venue_name,
                'venue_address': venue_address,
                'ticket_url': ticket_url,
            }

        print('Found ' + str(len(all_performers)) + ' performers from Ticketmaster!')
        print ('There were ' + str(error_count) + ' errors.')
