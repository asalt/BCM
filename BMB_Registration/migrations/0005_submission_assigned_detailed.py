# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-04 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMB_Registration', '0004_submission_assigned_ranks'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='assigned_detailed',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
