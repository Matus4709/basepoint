# Generated by Django 5.0.3 on 2024-05-15 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_remove_contacts_accounts_account_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactchat',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
