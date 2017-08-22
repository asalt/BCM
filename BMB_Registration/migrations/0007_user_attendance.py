# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-21 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BMB_Registration', '0006_user_last_login'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='attendance',
            field=models.CharField(choices=[('both', 'both'), ('thursday', 'thursday'), ('friday', 'friday')], default='both', max_length=20),
        ),
    ]