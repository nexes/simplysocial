# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-03 17:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_auto_20170703_1053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='posts',
        ),
    ]