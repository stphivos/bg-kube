# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from uuid import uuid4


class Profile(models.Model):
    user = models.OneToOneField(User)
    uuid = models.UUIDField(default=uuid4, editable=False)


class Todo(models.Model):
    user = models.ForeignKey(User, blank=True)
    title = models.CharField(max_length=200)
    tag = models.CharField(max_length=100, blank=True, null=True)
    priority = models.IntegerField()
