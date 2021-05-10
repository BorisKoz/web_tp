# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from ask_me import models

admin.site.register(models.Profile)
admin.site.register(models.Question)
admin.site.register(models.Answer)
admin.site.register(models.Tag)
admin.site.register(models.RateQuestion)
admin.site.register(models.RateAnswer)
# Register your models here.
