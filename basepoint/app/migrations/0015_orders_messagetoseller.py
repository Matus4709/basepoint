# Generated by Django 5.0.3 on 2024-05-02 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_orders_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='messageToSeller',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
