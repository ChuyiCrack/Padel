# Generated by Django 5.0.1 on 2024-02-09 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0037_match_want_to_start'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='Joined',
        ),
        migrations.AddField(
            model_name='match',
            name='Joined',
            field=models.ManyToManyField(blank=True, related_name='oponents_match', to='app1.account'),
        ),
    ]