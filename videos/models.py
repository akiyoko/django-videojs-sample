from django.db import models

class Video(models.Model):
    playlist_path = models.CharField(max_length=200)
