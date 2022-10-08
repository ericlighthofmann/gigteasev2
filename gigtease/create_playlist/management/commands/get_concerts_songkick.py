import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime
from tqdm import tqdm
import time
import math
import json
import pprint

from django.core.management.base import BaseCommand

from artist.models import Artist
from concert.models import Concert, Venue

class Command(BaseCommand):
    help = 'Uses the Songkick API to get concerts for each location.'

    def handle(self, *args, **options):

        def pretty_print(x):
            pp = pprint.PrettyPrinter(indent=1)
            x = pp.pprint(x)
            return x

        def jprint(x):
            x = json.dumps(x, indent=2)
            return x

        api_key = 'kOvxwC6MWevQ9d3h'
        # this is for user inputs
        city_name = 'San Diego'
        min_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        max_date = datetime.strftime(
            datetime.now() + relativedelta(months=1)
        , '%Y-%m-%d')

        # first get the metro from songkicks api (it uses this to search)
        location_url = 'https://api.songkick.com/api/3.0/search/locations.json?query='
        location_url = location_url + city_name + '&apikey=' + api_key
        location_url_response = requests.get(location_url)
        if location_url_response.ok:
            metro_id = location_url_response.json()['resultsPage']['results']['location'][0]['metroArea']['id']
        else:
            # TODO: return some error to the user saying we can't find their city
            pass

        # main api call
        api_call_data = [
            'apikey='+api_key,
            'per_page=50',
            'min_date='+min_date,
            'max_date='+max_date,
            'page=1',
        ]
        def api_call(modifiers):
            modified_url = base_url
            for modifier in modifiers:
                modified_url += '&' + modifier
            return requests.get(modified_url).json()

        # again, just get the total pages first then you gotta hit it every time for each page
        base_url = 'https://api.songkick.com/api/3.0/metro_areas/' + str(metro_id) + '/calendar.json?'
        apicall = api_call(api_call_data)
        for key, val in apicall.items():
            total_pages = math.ceil(val['totalEntries'] / 50)

        for page in tqdm(range(1, total_pages+1)):
            time.sleep(.5)
            api_call_data = api_call_data[:-1]
            api_call_data.append('page=' + str(page))
            events = api_call(api_call_data)
            results = events['resultsPage']['results']['event']

            print(jprint(results))
            assert False

            for result in results:
                if result['type'] == 'Concert':
                    artist_name = result['performance'][0]['artist']['displayName']
                    artist_id = result['performance'][0]['artist']['id']
                    venue_name = result['venue']['displayName']
                    venue_id = result['venue']['id']
                    concert_date = result['start']['date']
                    concert_id = result['performance'][0]['artist']['id']
                    concert_link = result['performance'][0]['artist']['uri']
                    #TODO: need to save this data and link it with the user?
                    #or save the query parameters to a user or something? i dunno
                    print(jprint(artist_name))

                    genre, created = Genre.objects.update_or_create(
                        name = genre
                    )
                    artist, created = Artist.objects.update_or_create(
                        songkick_id = artist_id,
                        defaults = {
                            'name': artist_name
                        }
                    )
                    venue, created = Venue.objects.update_or_create(
                        songkick_id = venue_id,
                        defaults = {
                            'name': venue_name
                        }
                    )
                    concert, created = Concert.objects.update_or_create(
                        songkick_id = concert_id,
                        defaults = {
                            'artist': artist,
                            'date': concert_date,
                            'link': concert_link,
                            'venue': venue,
                        }
                    )
                    #TODO: figure out how to filter by genres
                    #TODO: pass this data to the make_spotify_playlist management command
