from django.contrib import admin
from .models import PlaceCoordinates

@admin.register(PlaceCoordinates)
class PlaceCoordinatesAdmin(admin.ModelAdmin):
    pass
# Register your models here.
