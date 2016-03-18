# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noc', '0004_log'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='datetime',
            field=models.CharField(max_length=100),
        ),
    ]
