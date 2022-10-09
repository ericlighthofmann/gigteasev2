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

    help = 'Uses the SeatGeek API to get concerts for each location.'

    def handle(self, *args, **options):

        # DEFINE FAKE USER INPUTS
        time_period = 2
        distance = '15'
        location_zip = '92116'
        genres = 'alternative,rock'

        # configure user inputs for api call
        date_modifier = datetime.strftime(
            datetime.now() + relativedelta(weeks=int(time_period))
        , '%Y-%m-%d')
        distance = str(distance) + 'mi'
        # api key
        client_id = 'MTY5MTMzMjB8MTU1OTc4OTQxNi40Ng'

        api_call_data = [
            'geoip=' + location_zip + '&range=' + distance,
            'per_page=5000',
            'datetime_local.lt=' + date_modifier,
            'listing_count.gt=0',
            'genres.slug=' + genres,
            'taxonomies.name=concert'
        ]

        # this is our base call function
        base_url = 'https://api.seatgeek.com/2/events?client_id=' + client_id
        def api_call(modifiers):
            modified_url = base_url
            for modifier in modifiers:
                modified_url += '&' + modifier
            return {
                'results': requests.get(modified_url).json(),
                'query_url': modified_url,
            }

        # just getting the first page...5000 results should be enough
        # and every other page has an empty events array anyway
        events, query_url = api_call(api_call_data).values()
        all_performers = []
        for key, val in events.items():
            if key == 'events':
                for i, event in enumerate(val):
                    ticket_url = event['url']
                    # add artificial sleep to make the progress bar look cooler...
                    time.sleep(.02)
                    # celery
                    # progress_recorder.set_progress(i, len(val))
                    venue_name = event['venue']['name']
                    venue_address = event['venue']['address'] + ' ' + event['venue']['extended_address']
                    performers = event['performers']
                    for idx, performer in enumerate(performers):
                        current_performer = performer['name']
                        if current_performer not in all_performers:
                            all_performers.append(current_performer)

        query_results = {
            'all_performers': all_performers,

        }

        print('Found ' + str(len(all_performers)) + ' performers from Seatgeek!')
