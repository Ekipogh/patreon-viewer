from django.shortcuts import render
from .models import Movie

# Create your views here.

def index(request):
    movies = Movie.objects.all()
    return render(request=request, template_name='movies/index.html', context={'movies': movies})