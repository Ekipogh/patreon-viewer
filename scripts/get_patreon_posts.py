import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

patreon_home_page = "https://www.patreon.com/home"
baddmedicine_posts = "https://www.patreon.com/c/baddmedicine/posts"
baddmedicine_collections = "https://www.patreon.com/c/baddmedicine/collections"


def get_driver(url):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver


def login(driver):
    user_name = os.environ.get("PATREON_USER")
    password = os.environ.get("PATREON_PASS")
    # got to "/login" page
    driver.get("https://www.patreon.com/login")
    # find the "email" input field and enter the user name
    driver.find_element(By.NAME, "email").send_keys(user_name)
    # click submit button
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    # wait for the page to load
    driver.implicitly_wait(10)
    # find the "password" input field and enter the password
    driver.find_element(By.NAME, "current-password").send_keys(password)
    # click submit button
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    # wait for the page to load
    driver.implicitly_wait(30)


def test_get_first_post(driver):
    driver.get(baddmedicine_posts)

    # Wait for the page to load
    driver.implicitly_wait(10)

    # Get the first post
    post = driver.find_element(By.CSS_SELECTOR, "div[data-tag='post-card']")

    # Get the title of the post from a span with "post-title" data-tag
    title = post.find_element(
        By.CSS_SELECTOR, "span[data-tag='post-title']").text

    return title


def get_collections(driver):
    ignore_titles = ["Q & A with Badd Medicine", "Poll collection"]
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


def save_data(collections):
    if not os.path.exists("data"):
        os.makedirs("data")
    with open("data/collections.json", "w") as f:
        json.dump(collections, f, indent=4)


if __name__ == "__main__":

    driver = get_driver(patreon_home_page)

    collections = get_collections(driver)

    save_data(collections)
