# Generated by Django 5.0.1 on 2024-02-01 23:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0026_friend_requests'),
    ]

    operations = [
        migrations.CreateModel(
            name='notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=20)),
                ('message', models.TextField(max_length=50)),
            ],
        ),
    ]
