# Generated by Django 5.0.1 on 2024-01-13 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0006_account'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='user',
            new_name='owner',
        ),
    ]