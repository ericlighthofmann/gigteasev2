from django.shortcuts import render

def home(request):

    #TODO fill in with actual db queries
    playlists_created = 421
    songs_discovered = 12132
    concerts_found = 366

    return render(request, 'pages/home_landkit.html', {
        'playlists_created': playlists_created,
        'songs_discovered': songs_discovered,
        'concerts_found': concerts_found,
    })
