# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-04 09:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('axf', '0002_auto_20180704_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='nick_name',
            field=models.CharField(max_length=20, null=True, verbose_name='昵称'),
        ),
    ]
