# Generated by Django 5.0.3 on 2024-04-10 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_account_is_active_account_last_name_account_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='activation_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
