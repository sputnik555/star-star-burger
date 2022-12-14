from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static

from .models import Product, Order, OrderItems
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ValidationError


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address']

    def validate_order(self, order_items):
        self.is_valid(raise_exception=True)
        item_serializer = OrderItemSerializer(data=order_items, many=True, allow_empty=False)
        item_serializer.is_valid(raise_exception=True)


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ['product', 'quantity']


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    order_serializer = OrderSerializer(data=request.data)
    order_serializer.validate_order(request.data.get('products'))

    order = Order.objects.create(
        firstname=request.data['firstname'],
        lastname=request.data['lastname'],
        phonenumber=request.data['phonenumber'],
        address=request.data['address']
    )
    order_items = []
    for order_item in request.data['products']:
        product = Product.objects.get(id=order_item['product'])
        order_items.append(
            OrderItems(
                order=order,
                product=product,
                quantity=order_item['quantity'],
                price=product.price
            )
        )
    OrderItems.objects.bulk_create(order_items)
    return Response(OrderSerializer(order).data)

