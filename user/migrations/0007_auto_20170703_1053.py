# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-03 16:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_auto_20170703_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='posts',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='post.Posts'),
        ),
    ]
