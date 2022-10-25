from operator import itemgetter

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from coordinates.models import PlaceCoordinates
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderItems
import requests

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def fetch_coordinates(address):
    place_coordinates, created = PlaceCoordinates.objects.get_or_create(address=address)
    place_coordinates.fill_coordinates()
    if created or not place_coordinates.is_coordinates_filled():
        try:
            place_coordinates.fill_coordinates()
        except requests.RequestException:
            pass
    if place_coordinates.is_coordinates_filled():
        return (place_coordinates.latitude, place_coordinates.longitude)


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.prefetch_related('products').exclude(status=Order.DELIVERED)
    products_from_orders = OrderItems.objects.filter(order__in=orders).values_list('product', flat=True)
    restaurant_menu_items = RestaurantMenuItem.objects.filter(product__in=products_from_orders, availability=True)
    products_in_restaurants = {}
    for menu_item in restaurant_menu_items:
        products_in_restaurants.setdefault(menu_item.restaurant, set()).add(menu_item.product)

    for order in orders:
        order_coordinates = fetch_coordinates(order.address)
        print(order_coordinates)
        order.available_restaurants = []
        for restaurant, restaurant_products in products_in_restaurants.items():
            products_in_order = {item.product for item in order.products.all()}
            if products_in_order.issubset(restaurant_products):
                restaurant_coordinates = fetch_coordinates(restaurant.address)
                print(restaurant_coordinates)
                distance_to_restaurant = 0
                if restaurant_coordinates and order_coordinates:
                    distance_to_restaurant = distance.distance(order_coordinates, restaurant_coordinates).m
                order.available_restaurants.append(
                    {
                        'restaurant': restaurant,
                        'distance': distance_to_restaurant
                    }
                )
            order.available_restaurants.sort(key=itemgetter('distance'))

    return render(request, template_name='order_items.html', context={
        'order_items': orders
    })
