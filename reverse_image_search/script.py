import requests  # לביצוע ה-Web Scraping
from bs4 import BeautifulSoup  # לביצוע ה-Web Scraping
import io  # לעבודה עם תמונות
from google.cloud import vision  # ה-API עצמו
from google.oauth2 import service_account  # לאפשר את השימוש ב-API


class PriceWebsiteSource:

    def __init__(self, url, price_html_class, kbb=False, carsguide=False):
        # default is cars.com
        self.url = url
        self.price_html_class = price_html_class
        self.kbb = kbb  # requires different url formatting
        self.carsguide = carsguide  # requires additional "/price" for url
        self.all_car_models = ['Alfa Romeo', 'Audi', 'BMW', 'Chevrolet', 'Citroen', 'Chevrolet', 'Dacia', 'Daewoo',
                               'Dodge', 'Ferrari', 'Fiat', 'Ford', 'Honda', 'Hyundai', 'Jaguar', 'Jeep', 'Kia', 'Lada',
                               'Lancia', 'Land Rover', 'Lexus', 'Maserati', 'Mazda', 'Mercedes', 'Mitsubishi',
                               'Nissan', 'Opel', 'Peugeot', 'Porsche', 'Renault', 'Rover', 'Saab', 'Seat',
                               'Skoda', 'Subaru', 'Suzuki', 'Tata', 'Tesla', 'Toyota', 'Volkswagen', 'Volvo']
        self.all_car_models = [car.lower() for car in self.all_car_models]

    def get_price(self, car_model_lst):
        # (method is called only if car_model_lst is longer than 1)

        # For Example:
        # ['2021', 'audi', 'a4'], ['2020', 'audi', 'a4', 'allroad' ...]
        # ['toyota', 'corolla']

        for i in range(len(car_model_lst)):
            if car_model_lst[i].lower() in self.all_car_models:
                if i != len(car_model_lst) - 1:  # confirm there's a model, not just a company

                    # Tesla (cars.com) ends with: /tesla-model_3
                    # (and we usually take only 2 items)
                    # Goal: ["tesla", "model", "3"] -> ["tesla", "model_3"]
                    if car_model_lst[i].lower() == "tesla":
                        car_model_lst[i + 1] = car_model_lst[i + 1] + "_" + car_model_lst[i + 2]

                    if self.kbb:
                        url = f"{self.url}{car_model_lst[i]}/{car_model_lst[i + 1]}"  # "kbb.com/toyota/prius"

                    elif self.carsguide:
                        url = f"{self.url}{car_model_lst[i]}/{car_model_lst[i + 1]}/price"
                        # www.carsguide.com/toyota/prius/price

                    else:  # default, cars.com
                        url = f"{self.url}{car_model_lst[i]}-{car_model_lst[i + 1]}"
                        # https://www.cars.com/research/toyota-prius

                    html_result = requests.get(url)
                    doc = BeautifulSoup(html_result.text, 'html.parser')
                    try:
                        tag = doc.find_all(class_=self.price_html_class)[0].decode_contents()
                        tag_data = tag.split()

                        price = "-1"
                        for word in tag_data:
                            if '$' in word:
                                price = word
                                break

                        digits = "$,-–1234567890"
                        price = ''.join([char for char in price if char in digits])
                        return price, url

                    except IndexError:
                        return "-1", ""
                else:
                    return "-1", ""
        return "-1", ""


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
    if annotations.web_entities:
        # print('\n{} Web entities found: '.format(
        #       len(annotations.web_entities)))
        return annotations.web_entities


car_to_test = "tesla model 3".split()
carscom_site = PriceWebsiteSource("https://www.cars.com/research/", "accordion-spec-item-value")
print(carscom_site.get_price(car_to_test))


# carsguide_site = PriceWebsiteSource("https://www.carsguide.com.au/", "price", carsguide=True)
# kbb_site = PriceWebsiteSource("https://www.kbb.com/", "css-167zoth", kbb=True)
# print("kbb:", kbb_site.get_price(car_to_test))
# print("carsguide:", carsguide_site.get_price(car_to_test))
