# Generated by Django 5.0.1 on 2024-02-03 00:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0031_alter_match_ranked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend_notification',
            name='friend_to_add',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_request', to='app1.friend_requests'),
        ),
    ]
