# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noc', '0008_log_nocemp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='departments',
            field=models.CharField(max_length=255),
        ),
    ]
