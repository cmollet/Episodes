# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-04-21 15:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tvshow', '0011_auto_20190421_1010'),
    ]

    operations = [
        migrations.RenameField(
            model_name='show',
            old_name='imbd_id',
            new_name='imdb_id',
        ),
    ]
