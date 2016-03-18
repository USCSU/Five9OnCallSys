# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noc', '0002_remove_log_desc'),
    ]

    operations = [
        migrations.DeleteModel(
            name='log',
        ),
    ]
