# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2019-04-21 14:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tvshow', '0009_auto_20160823_2136'),
    ]

    operations = [
        migrations.RenameField(
            model_name='episode',
            old_name='episodeName',
            new_name='episode_name',
        ),
        migrations.RenameField(
            model_name='episode',
            old_name='firstAired',
            new_name='first_aired',
        ),
        migrations.RenameField(
            model_name='episode',
            old_name='tvdbID',
            new_name='tvdb_id',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='firstAired',
            new_name='first_aired',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='imbdID',
            new_name='imbd_id',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='runningStatus',
            new_name='running_status',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='seriesName',
            new_name='series_name',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='siteRating',
            new_name='site_rating',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='tvdbID',
            new_name='tvdb_id',
        ),
        migrations.RenameField(
            model_name='show',
            old_name='userRating',
            new_name='user_rating',
        ),
    ]
