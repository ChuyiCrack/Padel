# Generated by Django 5.0.1 on 2024-01-25 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0020_remove_match_looser_remove_match_winner_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='res_creator',
            field=models.CharField(default='', max_length=15),
        ),
        migrations.AddField(
            model_name='result',
            name='res_joined',
            field=models.CharField(default='', max_length=15),
        ),
    ]
