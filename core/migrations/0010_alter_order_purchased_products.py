# Generated by Django 5.0.3 on 2024-05-09 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_ordered_products_order_purchased_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='purchased_products',
            field=models.ManyToManyField(related_name='orders', through='core.OrderItem', to='core.product'),
        ),
    ]
