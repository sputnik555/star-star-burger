# Generated by Django 3.2.15 on 2022-10-17 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0038_order_orderitems'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='last_name',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='phone_number',
            new_name='phonenumber',
        ),
    ]
