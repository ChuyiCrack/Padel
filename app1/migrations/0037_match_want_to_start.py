# Generated by Django 5.0.1 on 2024-02-09 03:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0036_alter_account_party_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='want_to_start',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
