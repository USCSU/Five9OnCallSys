# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20160321_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='phone',
            field=models.EmailField(default='9254137056@txt.att.net', max_length=50),
            preserve_default=False,
        ),
    ]
