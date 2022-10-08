from django.shortcuts import render

from create_playlist.tasks import create_spotify_playlist

def playlist_dashboard(request, task_id):
    result = create_spotify_playlist.AsyncResult(task_id)
    band_song_results = result.get()['band_song_dict']

    for key, val in band_song_results.items():
        print (key, val)

    return render(request, 'pages/playlist-dashboard.html', {
        'task_id': task_id,
        'band_song_results': band_song_results,
    })
