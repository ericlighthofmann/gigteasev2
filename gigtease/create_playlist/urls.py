from django.urls import path

from . import views

urlpatterns = [
    # UI screen for collecting parameters for playlist before creation
    path("create-playlist/", views.create_playlist, name="create_playlist"),
    path("write-payload-and-task-id-to-db/", views.write_payload_and_task_id_to_db, name="write_padload_and_task_id_to_db"),

    # view/template for progress bars and ops in progress
    path('create-playlist-in-progress/<str:task_id>/', views.create_playlist_in_progress,
         name='create_playlist_in_progress'),

    # server side exchange of code for access token (spotify)
    path('get-access-token-spotify/', views.get_access_token_spotify),

    # urls for vendor api queries
    path('get-seatgeek-query-results/<str:task_id>/', views.get_seatgeek_query_results),

    # url for creating spotify playlist
    path('kick-off-spotify/<str:seatgeek_task_id>/', views.kick_off_spotify),
    path('get-spotify-playlist-results/<str:task_id>/', views.get_spotify_playlist_results),

    # reset tasks for reset dev button
    path('reset-create-playlist-tasks/', views.reset_create_playlist_tasks),
]
