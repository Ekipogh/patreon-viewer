import os
import sys
import json
import django
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

patreon_home_page = "https://www.patreon.com/home"
baddmedicine_collections = "https://www.patreon.com/c/baddmedicine/collections"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patreon_viewer.settings')

def get_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


def get_collections(driver):
    ignore_titles = ["Q & A with Badd Medicine", "Poll collection",
                     "Trailer Premiers", "Monthly Schedule update"]
    # [ {title: "title", thumbnail: "thumbnail.jpg"  url: "url"}, ...]
    collections = []
    driver.get(baddmedicine_collections)
    driver.implicitly_wait(50)
    # keep scrolling to the bottom of the page until all posts are loaded
    page_height = driver.execute_script("return document.body.scrollHeight")
    previous_page_height = 0
    while page_height != previous_page_height:
        previous_page_height = page_height
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        try:
            WebDriverWait(driver, 10).until(lambda driver: driver.execute_script(
                "return document.body.scrollHeight") > page_height)
        except:
            break
        page_height = driver.execute_script(
            "return document.body.scrollHeight")
    collections_xpath = '/html/body/div[1]/main/div[1]/div/div[3]/div/div[2]'
    # second child element is the list of collections
    collection_list = driver.find_element(
        By.XPATH, collections_xpath)

    collection_elements = collection_list.find_elements(
        By.CSS_SELECTOR, ":scope > div")
    for collection in collection_elements:
        if collection.text != "":
            # p tag with data-tag="box-collection-title" is the title
            title = collection.find_element(By.TAG_NAME, "strong").text
            if title in ignore_titles:
                continue
            # a tag is the url
            url = collection.find_element(
                By.TAG_NAME, "a").get_attribute("href")
            # background-image of a div with data-tag="box-collection-thumbnail" is the thumbnail
            thumbnail = collection.find_element(
                By.CSS_SELECTOR, "div[data-tag='box-collection-thumbnail']").value_of_css_property("background-image")
            clean_thumbnail = thumbnail.replace(
                'url("', "").replace('")', "")
            collections.append(
                {"title": title, "thumbnail": clean_thumbnail, "url": url})
            print(f"Adding collection: {title}")

    return collections


def get_genre_from_omdb(title):
    omdb_key = os.environ.get('OMDB_API_KEY')
    url = f"http://www.omdbapi.com/?apikey={omdb_key}&t={title}"
    response = requests.get(url)
    data = response.json()
    if data.get('Response') == 'True':
        genre = data.get('Genre')
        genre_list = genre.split(",")
        if len(genre_list) == 1 and genre_list[0] == "N/A":
            return None
        return genre_list
    return None


def get_type_from_omdb(title):
    omdb_key = os.environ.get('OMDB_API_KEY')
    url = f"http://www.omdbapi.com/?apikey={omdb_key}&t={title}"
    response = requests.get(url)
    data = response.json()
    if data.get('Response') == 'True':
        return data.get('Type')
    return None

def get_release_year_from_omdb(title):
    omdb_key = os.environ.get('OMDB_API_KEY')
    url = f"http://www.omdbapi.com/?apikey={omdb_key}&t={title}"
    response = requests.get(url)
    data = response.json()
    if data.get('Response') == 'True':
        return data.get('Year')
    return None

def parse_id(url):
    return url.split('/')[-1]


def update_django_database(collections):
    not_found = set()
    from movies.models import Movie, Genre
    for collection in collections:
        title = collection['title']
        patreon_title = title
        thumbnail = collection['thumbnail']
        url = collection['url']
        genre_list = get_genre_from_omdb(title)
        genres = []
        if not genre_list:
            print(f"Could not find genre for {title}")
            print(f"Might need to fix the title")
            not_found.add(title)
            genre_list = ["Uncategorized"]

        for genre in genre_list:
            genre_obj, created = Genre.objects.get_or_create(name=genre)
            genres.append(genre_obj)
            if created:
                print(f"---> Added genre: {genre}")
        media_type = get_type_from_omdb(title)
        if not media_type:
            print(f"Could not find type for {title}")
            print(f"Might need to fix the title")
            media_type = "movie" # default to movie
            not_found.add(title)

        release_year = get_release_year_from_omdb(title)
        if not release_year:
            print(f"Could not find release year for {title}")
            print(f"Might need to fix the title")
            release_year = None
            not_found.add(title)

        movie, created = Movie.objects.get_or_create(
            title=title)
        is_movie_title_fixed = not created and movie.title != patreon_title
        if created or is_movie_title_fixed:
            patreon_id = parse_id(url)
            movie.patreon_id = patreon_id
            movie.patreon_title = patreon_title
            movie.thumbnail = thumbnail
            movie.post_url = url
            movie.type = media_type
            movie.release_year_range = release_year
            movie.genres.set(genres)
            movie.save()
            print(f"Added movie: {title}")
    print(f"Movies not found: {not_found}")
    if not_found:
        fix_titles(not_found)
    return

def fix_titles(not_found):
    from movies.models import Movie
    for title in not_found:
        movie = Movie.objects.get(title=title)
        try_to_fix_genres_and_type(movie)
        movie.save()
        print(f"Fixed title for {title}")
    return

def try_to_fix_genres_and_type(movie):
    fixed_names = json.load(open("scripts/data/fixed_names.json"))
    if movie.title in fixed_names:
        movie.title = fixed_names[movie.title]
    else:
        fixed_title = input(f"Fix title for {movie.title}: ")
        movie.title = fixed_title
    from movies.models import Genre
    genre_list = get_genre_from_omdb(movie.title)
    if not genre_list:
        print(f"Could not find genre for {movie.title}")
    genres = []
    for genre in genre_list:
        genre_obj, created = Genre.objects.get_or_create(name=genre)
        genres.append(genre_obj)
        if created:
            print(f"---> Added genre: {genre}")
    media_type = get_type_from_omdb(movie.title)
    if not media_type:
        print(f"Could not find type for {movie.title}")
    movie.type = media_type
    movie.genres.set(genres)
    return

def parse_patreon():
    # get collections from baddmedicine Patreon page
    driver = get_driver(patreon_home_page)
    collections = get_collections(driver)
    driver.quit()
    print(f"Collected {len(collections)} collections")
    return collections


if __name__ == "__main__":
    # setup django
    django.setup()
    clean_database = True
    if clean_database:
        from movies.models import Movie, Genre
        Movie.objects.all().delete()
        Genre.objects.all().delete()
    collections = parse_patreon()
    # add collections to database
    update_django_database(collections)
