# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-03 15:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20170703_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='posts',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='post.Posts'),
        ),
    ]
