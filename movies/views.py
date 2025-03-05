from django.shortcuts import render
from .models import Movie, Genre

# Create your views here.


def index(request):
    type = request.GET.get('type') if request.GET.get('type') else 'movie'
    title = request.GET.get('title')
    genre = request.GET.get('genre')
    all_movies = Movie.objects.all()
    all_genres = Genre.objects.all()
    start_year = request.GET.get('start_year')
    end_year = request.GET.get('end_year')
    genre_list = []
    movies = all_movies
    if type:
        movies = movies.filter(type=type)
    if title:
        movies = movies.filter(title__icontains=title)
    if genre:
        genre_list = genre.split(',')
        for g in genre_list:
            g = g.strip()
            movies = movies.filter(genres__name__icontains=g)
    all_years = set()
    for movie in movies:
        if movie.release_year_range:
            if "-" in movie.release_year_range:
                start_year, end_year = movie.release_year_range.split('-')
                all_years.add(int(start_year))
                all_years.add(int(end_year))
            else:
                all_years.add(int(movie.release_year_range))
    if start_year or end_year:
        movies = [movie for movie in movies if movie.is_in_range(
            int(start_year) if start_year else None, int(end_year) if end_year else None)]
    return render(
        request=request,
        template_name='movies/index.html',
        context={
            'movies': movies,
            'all_movies': all_movies,
            'all_genres': all_genres,
            'selected_genre': genre_list,
            'selected_title': title,
            "all_years": sorted(all_years),
            "selected_start_year": start_year,
            "selected_end_year": end_year,
        }
    )
