# Generated by Django 5.0.1 on 2024-01-21 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0016_alter_match_creator_remove_match_joined_match_joined'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='started',
            field=models.BooleanField(default=False),
        ),
    ]
