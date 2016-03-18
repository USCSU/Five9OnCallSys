# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noc', '0003_delete_log'),
    ]

    operations = [
        migrations.CreateModel(
            name='log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('ticketnumber', models.CharField(max_length=50)),
                ('oncallUser', models.CharField(max_length=255)),
                ('departments', models.CharField(max_length=100)),
            ],
        ),
    ]
