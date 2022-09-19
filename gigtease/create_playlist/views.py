from django.shortcuts import render

def create_playlist(request):

    return render(request, 'pages/home_landkit.html', {
        'playlists_created': playlists_created,
        'songs_discovered': songs_discovered,
        'concerts_found': concerts_found,
    })
