# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-14 17:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pfx', '0030_member_commission_received'),
    ]

    operations = [
        migrations.AlterField(
            model_name='igpl',
            name='opening_ref',
            field=models.CharField(max_length=8),
        ),
    ]