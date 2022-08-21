import argparse
import requests  # לביצוע ה-Web Scraping
from bs4 import BeautifulSoup  # לביצוע ה-Web Scraping
import io  # לעבודה עם תמונות
from google.cloud import vision  # ה-API עצמו
from google.oauth2 import service_account  # לאפשר את השימוש ב-API


def annotate(path):
    """Returns web annotations given the path to an image."""
    creds = service_account.Credentials.from_service_account_file('google_cloud.json')
    client = vision.ImageAnnotatorClient(
        credentials=creds,
    )

    if path.startswith('http') or path.startswith('gs:'):
        image = vision.Image()
        image.source.image_uri = path

    else:
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

    web_detection = client.web_detection(image=image).web_detection

    return web_detection



def report(annotations):
    """Prints detected features in the provided web annotations."""
    if annotations.pages_with_matching_images:
        print('\n{} Pages with matching images retrieved'.format(
            len(annotations.pages_with_matching_images)))

        for page in annotations.pages_with_matching_images:
            print('Url   : {}'.format(page.url))

    if annotations.full_matching_images:
        print('\n{} Full Matches found: '.format(
              len(annotations.full_matching_images)))

        for image in annotations.full_matching_images:
            print('Url  : {}'.format(image.url))

    if annotations.partial_matching_images:
        print('\n{} Partial Matches found: '.format(
              len(annotations.partial_matching_images)))

        for image in annotations.partial_matching_images:
            print('Url  : {}'.format(image.url))

    if annotations.web_entities:
        print('\n{} Web entities found: '.format(
              len(annotations.web_entities)))

        for entity in annotations.web_entities:
            print('Score      : {}'.format(entity.score))
            print('Description: {}'.format(entity.description))


report(annotate('car_example.jpg'))


