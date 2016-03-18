# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='department',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('departmentid', models.IntegerField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='employee',
            fields=[
                ('firstName', models.CharField(max_length=50)),
                ('lastName', models.CharField(max_length=50)),
                ('number', models.IntegerField(null=True, blank=True)),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=20, null=True, blank=True)),
                ('state', models.CharField(max_length=10, null=True, blank=True)),
                ('zipcode', models.IntegerField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254)),
                ('mobile', models.CharField(max_length=20)),
                ('employeeid', models.IntegerField(serialize=False, primary_key=True)),
                ('manager', models.BooleanField()),
                ('department', models.ForeignKey(to='manager.department')),
            ],
        ),
        migrations.CreateModel(
            name='log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('department', models.CharField(max_length=20)),
                ('manager', models.CharField(max_length=20)),
                ('startdate', models.DateField()),
                ('enddate', models.DateField()),
                ('oncallUser', models.CharField(max_length=255)),
                ('logtime', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='onDuty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('department', models.ForeignKey(to='manager.department')),
                ('employee', models.ForeignKey(to='manager.employee')),
            ],
        ),
    ]
