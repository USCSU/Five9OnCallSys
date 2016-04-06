# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_employee_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='enddate',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='log',
            name='startdate',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='onduty',
            name='endDate',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='onduty',
            name='startDate',
            field=models.DateTimeField(),
        ),
    ]
