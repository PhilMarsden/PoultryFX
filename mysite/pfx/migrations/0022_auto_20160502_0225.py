# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 01:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pfx', '0021_auto_20160502_0135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individualpl',
            name='commission',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='individualpl',
            name='fun_fund',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='individualpl',
            name='profit',
            field=models.FloatField(default=0),
        ),
    ]
