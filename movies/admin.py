from django.contrib import admin

# Register your models here.

from .models import Movie, Genre

class MovieAdmin(admin.ModelAdmin):
    search_fields = ('title', 'patreon_title')

admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
