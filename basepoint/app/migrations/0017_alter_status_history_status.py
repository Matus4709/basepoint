# Generated by Django 5.0.3 on 2024-05-11 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_status_history_id_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status_history',
            name='status',
            field=models.CharField(max_length=100),
        )
    ]
