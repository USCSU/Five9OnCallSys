# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noc', '0005_auto_20160316_0028'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='escalate',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
