# Generated by Django 5.0.3 on 2024-04-11 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_account_activation_token_alter_account_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='reset_password_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
