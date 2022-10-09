from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import Coalesce

from gigtease.create_playlist.models import CreatedPlaylist


def home(request):
    created_playlists_qs = CreatedPlaylist.objects.all()
    starting_playlists_created_val = 93
    playlists_created = created_playlists_qs.count() + starting_playlists_created_val

    songs_discovered = created_playlists_qs.aggregate(
        song_count=Coalesce(Sum('song_count'), 0),
    ).get('song_count')
    concerts_found = created_playlists_qs.aggregate(
        concert_count=Coalesce(Sum('concert_count'), 0)
    ).get('concert_count')

    songs_discovered += (starting_playlists_created_val * 20)
    concerts_found += (starting_playlists_created_val * 15)

    return render(request, 'pages/home_landkit.html', {
        'playlists_created': playlists_created,
        'songs_discovered': songs_discovered,
        'concerts_found': concerts_found,
    })
