import os
import sys
import django
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patreon_viewer.settings')

django.setup()

from movies.models import Movie, Genre

def set_genres():
    omdb_api_key = os.environ.get('OMDB_API_KEY')
    omdb_url = f"http://www.omdbapi.com/?apikey={omdb_api_key}&t="

    # add Uncategorized genre if doesn't exist
    if not Genre.objects.filter(name="Uncategorized").exists():
        Genre.objects.create(name="Uncategorized")

    for movie in Movie.objects.all():
        genre = "Uncategorized"
        movie_genres = movie.genres
        if not len(movie_genres.all()) or movie_genres.all()[0].name == "Uncategorized":
            response = requests.get(omdb_url + movie.title)
            data = response.json()
            genre = data.get('Genre', "Uncategorized")
            genre, _ = Genre.objects.get_or_create(name=genre)
            movie.genre = genre
            movie.save()
            print(f"Setting genre for {movie.title} to {genre}")

if __name__ == '__main__':
    set_genres()
