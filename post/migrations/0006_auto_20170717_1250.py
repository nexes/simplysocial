# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-17 18:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0005_auto_20170707_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='image_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
