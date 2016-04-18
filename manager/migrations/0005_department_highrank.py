# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_auto_20160405_2342'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='highRank',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
    ]
