# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='address',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='city',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='mobile',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='number',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='state',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='zipcode',
        ),
    ]
