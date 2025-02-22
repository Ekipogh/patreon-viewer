import os
import sys
import json
import django
from movies.models import Movie

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patreon_viewer.settings')

django.setup()


def populate():
    with open('data/collections.json') as f:
        data = json.load(f)
        for movie in data:
            # check if movie already exists
            if not Movie.objects.filter(title=movie['title']).exists():
                Movie.objects.create(
                    title=movie['title'], post_url=movie['url'], thumbnail=movie['thumbnail'])


if __name__ == '__main__':
    populate()
