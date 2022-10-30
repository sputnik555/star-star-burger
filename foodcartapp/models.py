import datetime

from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    DELIVERED = 'D'
    IN_PROGRESS = 'P'
    NEW = 'N'
    CARD = 'CARD'
    CASH = 'CASH'
    STATUS_CHOICES = [
        (NEW, 'Новый'),
        (IN_PROGRESS, 'Выполняется'),
        (DELIVERED, 'Доставлен')
    ]
    PAYMENT_METHOD_CHOICES = [
        (CARD, 'Картой'),
        (CASH, 'Наличными')
    ]

    firstname = models.CharField(max_length=100, verbose_name='Фамилия')
    lastname = models.CharField(max_length=100, verbose_name='Имя')
    phonenumber = PhoneNumberField(verbose_name='Номер телефона')
    address = models.CharField(max_length=200, verbose_name='Адрес доставки')
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=NEW,
        db_index=True,
        verbose_name='Статус'
    )
    payment_method = models.CharField(
        max_length=4,
        choices=PAYMENT_METHOD_CHOICES,
        default=CASH,
        db_index=True,
        verbose_name='Способ оплаты'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name="Ресторан",
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата создания',
        blank=True,
        null=True
    )
    called_at = models.DateTimeField(verbose_name='Дата звонка', blank=True, null=True)
    delivered_at = models.DateTimeField(verbose_name='Дата доставки', blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def price(self):
        order_price = self.items.aggregate(total_price=Sum(F('quantity')*F('price'))).get('total_price')
        return order_price


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'Строка заказа'
        verbose_name_plural = 'Строки заказа'

