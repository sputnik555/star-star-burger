import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from coordinates.yandex_geo_api import get_coordinates


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
        auto_now=True,
    )

    def fill_coordinates(self):
        update_time_delta = datetime.timedelta(hours=settings.COORDINATES_LIFETIME)
        if self.is_coordinates_filled and timezone.now() - self.update_date < update_time_delta:
            return
        coordinates = get_coordinates(self.address)
        if coordinates:
            self.longitude, self.latitude = coordinates
            self.save()

    @property
    def is_coordinates_filled(self):
        return self.longitude is not None and self.latitude is not None
