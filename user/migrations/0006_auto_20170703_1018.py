# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-03 16:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20170703_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='posts',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='post.Posts'),
        ),
    ]
