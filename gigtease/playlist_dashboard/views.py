from django.shortcuts import render

from gigtease.create_playlist.tasks import create_spotify_playlist

def playlist_dashboard(request, task_id):
    result = create_spotify_playlist.AsyncResult(task_id)
    band_song_results = result.get()['band_song_dict']

    return render(request, 'pages/playlist-dashboard.html', {
        'task_id': task_id,
        'band_song_results': band_song_results,
    })
