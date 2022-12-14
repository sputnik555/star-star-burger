# Generated by Django 3.2.15 on 2022-10-25 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PlaceCoordinates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True, verbose_name='адрес')),
                ('latitude', models.DecimalField(decimal_places=14, max_digits=16, null=True, verbose_name='Широта')),
                ('longitude', models.DecimalField(decimal_places=14, max_digits=17, null=True, verbose_name='Долгота')),
                ('update_date', models.DateTimeField(null=True, verbose_name='Дата обновления')),
            ],
        ),
    ]
