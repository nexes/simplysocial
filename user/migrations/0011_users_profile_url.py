# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-20 01:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_auto_20170717_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='profile_url',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
