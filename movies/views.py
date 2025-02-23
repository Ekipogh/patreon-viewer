from django.shortcuts import render
from .models import Movie, Genre

# Create your views here.


def index(request):
    type = request.GET.get('type') if request.GET.get('type') else 'movie'
    title = request.GET.get('title')
    genre = request.GET.get('genre')
    all_movies = Movie.objects.all()
    all_genres = Genre.objects.all()
    genre_list = []
    movies = all_movies
    if type:
        movies = movies.filter(type=type)
    if title:
        movies = movies.filter(title__icontains=title)
    if genre:
        genre_list = genre.split(',')
        for g in genre_list:
            movies = movies.filter(genres__name__icontains=g)
    return render(request=request, template_name='movies/index.html', context={'movies': movies, 'all_movies': all_movies, 'all_genres': all_genres, 'selected_genre': genre_list, 'selected_title': title})
