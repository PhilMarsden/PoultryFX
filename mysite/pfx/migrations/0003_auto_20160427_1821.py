# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-27 17:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pfx', '0002_auto_20160427_1819'),
    ]

    operations = [
        migrations.RenameField(
            model_name='individualcashtransactions',
            old_name='member_id',
            new_name='member',
        ),
    ]
