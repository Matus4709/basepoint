# Generated by Django 5.0.3 on 2024-05-02 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_product_has_orders_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='delivery',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]