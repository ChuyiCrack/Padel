# Generated by Django 5.0.1 on 2024-02-03 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0030_match_ranked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='ranked',
            field=models.BooleanField(),
        ),
    ]