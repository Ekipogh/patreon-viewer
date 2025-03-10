from datetime import datetime
from django.db import models

# Create your models here.


class Movie(models.Model):
    RELEASE_SEPARATOR = '–'
    title = models.CharField(max_length=200, unique=True)
    patreon_title = models.CharField(max_length=200, blank=True)
    post_url = models.URLField()
    thumbnail = models.URLField(max_length=500)
    genres = models.ManyToManyField('Genre', related_name='movies', blank=True)
    TYPE_CHOICES = (
        ('movie', 'Movie'),
        ('series', 'Series'),
    )
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, default='movie')
    patreon_id = models.IntegerField(unique=True, blank=True, null=True)
    release_year_range = models.CharField(max_length=9, blank=True, null=True)

    def is_in_range(self, year_start, year_end):
        current_year = datetime.now().year
        if not self.release_year_range:
            return False

        try:
            if Movie.RELEASE_SEPARATOR in self.release_year_range:
                movie_year_start_string, movie_year_end_string = self.release_year_range.split(
                    Movie.RELEASE_SEPARATOR)
                movie_year_start = int(
                    movie_year_start_string) if movie_year_start_string else current_year
                movie_year_end = int(
                    movie_year_end_string) if movie_year_end_string else current_year
            else:
                movie_year_start = movie_year_end = int(
                    self.release_year_range)
        except ValueError:
            return False

        is_before_end = year_end is None or movie_year_end <= year_end
        is_after_start = year_start is None or movie_year_start >= year_start

        return is_before_end and is_after_start

    def __str__(self):
        return self.title

    def genre_text(self):
        return ', '.join([g.name for g in self.genres.all()])

    class Meta:
        ordering = ['-patreon_id']


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
