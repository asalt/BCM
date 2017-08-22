# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-22 18:00
from __future__ import unicode_literals

import BMB_Registration.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BMB_Registration', '0009_auto_20170725_1528'),
    ]

    operations = [
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload', models.FileField(upload_to=BMB_Registration.models.user_directory_path)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='BMB_Registration.User')),
            ],
        ),
    ]
