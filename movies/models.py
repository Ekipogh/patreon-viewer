from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200, unique=True)
    post_url = models.URLField()
    thumbnail = models.URLField()
    genres = models.ManyToManyField('Genre', related_name='movies')

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
