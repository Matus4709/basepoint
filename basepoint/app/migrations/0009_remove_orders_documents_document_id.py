# Generated by Django 5.0.3 on 2024-05-01 12:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_orders_seller'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orders',
            name='documents_document_id',
        ),
    ]
