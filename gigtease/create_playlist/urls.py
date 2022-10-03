from django.urls import path

from . import views

urlpatterns = [
    # UI screen for collecting parameters for playlist before creation
    path("create-playlist/", views.create_playlist, name="create_playlist"),

    # view/template for progress bars and ops in progress
    path('create-playlist-in-progress/<str:task_id>/', views.create_playlist_in_progress,
         name='create_playlist_in_progress'),

    # server side exchange of code for access token (spotify)
    path('get-access-token-spotify/', views.get_access_token_spotify),

    # urls for vendor api queries
    path('kick-off-seatgeek-api-query/', views.kick_off_seatgeek_api_query),
]
