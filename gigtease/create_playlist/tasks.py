import time
from datetime import datetime

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from celery_progress.backend import ProgressRecorder
from dateutil.relativedelta import relativedelta

logger = get_task_logger(__name__)

@shared_task(bind=True)
def query_seatgeek_api(self, location_zip, location_name, genres, start_date, end_date, distance, auth_token):
    progress_recorder = ProgressRecorder(self)

    # configure user inputs for api call
    distance = str(distance) + 'mi'
    # api key
    client_id = 'MTY5MTMzMjB8MTU1OTc4OTQxNi40Ng'

    api_call_data = [
        'geoip=' + location_zip + '&range=' + distance,
        'per_page=5000',
        'datetime_local.gt=' + start_date,
        'datetime_local.lt=' + end_date,
        #'listing_count.gt=0',
        'taxonomies.name=concert'
    ]
    api_call_data.append(
        'genres.slug=' + ','.join(genres)
    )

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
            for i, event in enumerate(val):
                # add artificial sleep to make the progress bar look cooler...
                time.sleep(.02)
                progress_recorder.set_progress(i, len(val))
                ticket_url = event['url']
                date = event['datetime_local']
                venue_name = event['venue']['name']
                venue_address = event['venue']['address'] + ' ' + event['venue']['extended_address']
                performers = event['performers']
                for idx, performer in enumerate(performers):
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
    logger.info('Found ' + str(len(all_performers)) + ' performers from Seatgeek!')
    return {
        'event_info': event_info,
        'all_performers': all_performers, 'auth_token': auth_token,
        'location_zip': location_zip, 'location_name': location_name, 'genres': genres,
        'start_date': start_date, 'end_date': end_date, 'distance': distance,
    }
