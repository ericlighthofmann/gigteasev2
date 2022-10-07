from django.db import models


class Playlist(models.Model):
    task_id = models.CharField(max_length=255)
    location_zip = models.IntegerField()
    location_name = models.CharField(max_length=255)
    genres = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    distance = models.IntegerField()
    auth_token = models.CharField(max_length=255)
