# Generated by Django 5.0.3 on 2024-05-09 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_order_purchased_products'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='purchased_products',
        ),
    ]
