from django.urls import path

from . import views

urlpatterns = [
    path("create-playlist/", views.create_playlist, name="create_playlist"),
]
