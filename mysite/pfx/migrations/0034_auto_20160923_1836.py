# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-23 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pfx', '0033_individualpl_net_return'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradeemail',
            name='message_id',
            field=models.CharField(max_length=255),
        ),
    ]
