# Generated by Django 3.2.15 on 2022-10-23 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_auto_20221019_0232'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('N', 'Новый'), ('P', 'Выполняется'), ('D', 'Доставлен')], db_index=True, default='N', max_length=1, verbose_name='Статус'),
        ),
    ]