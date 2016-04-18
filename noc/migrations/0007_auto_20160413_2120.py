# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noc', '0006_log_escalate'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='bridge',
            field=models.CharField(default=-1276, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='log',
            name='management',
            field=models.CharField(default=['CS', 'OPS', 'Scott'], max_length=255),
            preserve_default=False,
        ),
    ]
