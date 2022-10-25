import datetime

from django.db import models
import requests
from django.conf import settings
from django.utils import timezone


def get_coordinates_from_yandex(address):
    apikey = settings.YANDEX_GEO_TOKEN
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


class PlaceCoordinates(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True
    )
    latitude = models.DecimalField(
        verbose_name='Широта',
        max_digits=16,
        decimal_places=14,
        null=True
    )
    longitude = models.DecimalField(
        verbose_name='Долгота',
        max_digits=17,
        decimal_places=14,
        null=True
    )
    update_date = models.DateTimeField(
        verbose_name='Дата обновления',
        null=True,
    )

    def fill_coordinates(self):
        update_time_delta = datetime.timedelta(hours=settings.COORDINATES_LIFETIME)
        if self.update_date and timezone.now() - self.update_date < update_time_delta:
            return

        coordinates = get_coordinates_from_yandex(self.address)
        if coordinates:
            self.longitude, self.latitude = coordinates
            self.update_date = timezone.now()
            self.save()

    def is_coordinates_filled(self):
        return self.longitude is not None and self.latitude is not None

