# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-28 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pfx', '0009_auto_20160427_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='igpl',
            name='closed_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='igpl',
            name='opening_date',
            field=models.DateField(),
        ),
    ]
