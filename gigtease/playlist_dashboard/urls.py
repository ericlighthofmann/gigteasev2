from django.urls import path

from . import views

urlpatterns = [
    # view/template for progress bars and ops in progress
    path('playlist-dashboard/<str:task_id>/', views.playlist_dashboard,
         name='playlist_dashboard'),
]
