from django.db import models


class PlaylistInProgress(models.Model):
    task_id = models.CharField(max_length=255)
    location_zip = models.IntegerField()
    location_name = models.CharField(max_length=255)
    genres = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    distance = models.IntegerField()
    auth_token = models.CharField(max_length=255)


class CreatedPlaylist(models.Model):
    """
    This is for metadata on the front page - displaying how many playlists, songs, and concerts have been
    created.
    """
    song_count = models.IntegerField()
    concert_count = models.IntegerField()
