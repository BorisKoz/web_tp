# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-05-09 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ask_me', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='answer_text',
            field=models.TextField(default=''),
        ),
    ]
