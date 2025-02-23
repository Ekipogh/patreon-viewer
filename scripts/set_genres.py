import os
import sys
import json
import django
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patreon_viewer.settings')

django.setup()

from movies.models import Movie, Genre

def set_genres():
    omdb_api_key = os.environ.get('OMDB_API_KEY')
    omdb_url = f"http://www.omdbapi.com/?apikey={omdb_api_key}&t="

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    not_found = []

    # add Uncategorized genre if doesn't exist
    if not Genre.objects.filter(name="Uncategorized").exists():
        Genre.objects.create(name="Uncategorized")

    for movie in Movie.objects.all():
        movie_genres = movie.genres
        if not len(movie_genres.all()) or movie_genres.all()[0].name == "Uncategorized":
            response = requests.get(omdb_url + movie.title)
            data = response.json()
            if data.get('Response') == 'False':
                print(f"Error: {data.get('Error')} for {movie.title}")
                not_found.append(movie.title)
                continue
            genre_string = data.get('Genre')
            genres = genre_string.split(",")
            if len(genres) == 1 and genres[0] == "N/A":
                genres = ["Uncategorized"]
            for genre in genres:
                genre = genre.strip()
                genre_obj, created = Genre.objects.get_or_create(name=genre)
                movie.genres.add(genre_obj)
                movie.save()
                print(f"Added genre {genre} to {movie.title}")
    print(f"Movies not found: {not_found}")
    json.dump(not_found, open(os.path.join(data_dir, 'not_found.json'), 'w'))


def clean_genres():
    for movie in Movie.objects.all():
        movie.genres.clear()
        movie.save()

def clean_patreon_titles():
    for movie in Movie.objects.all():
        movie.patreon_title = movie.title
        movie.save()


if __name__ == '__main__':
    set_genres()
    # clean_genres()
    # clean_patreon_titles()
