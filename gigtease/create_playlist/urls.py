from django.urls import path

from . import views

urlpatterns = [
    path("create-playlist/", views.create_playlist, name="create_playlist"),
    # server side exchange of code for access token (spotify)
    path('get-access-token-spotify/', views.get_access_token_spotify),
]
