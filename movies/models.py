from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200, unique=True)
    patreon_title = models.CharField(max_length=200, blank=True)
    post_url = models.URLField()
    thumbnail = models.URLField(max_length=500)
    genres = models.ManyToManyField('Genre', related_name='movies', blank=True)

    def __str__(self):
        return self.title

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
