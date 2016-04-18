# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noc', '0009_auto_20160414_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='departments',
            field=models.TextField(max_length=255),
        ),
        migrations.AlterField(
            model_name='log',
            name='management',
            field=models.TextField(max_length=255),
        ),
        migrations.AlterField(
            model_name='log',
            name='oncallUser',
            field=models.TextField(max_length=255),
        ),
    ]
