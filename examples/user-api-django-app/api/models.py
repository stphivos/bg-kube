# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from uuid import uuid4


class Profile(models.Model):
    user = models.OneToOneField(User)
    uuid = models.UUIDField(default=uuid4, editable=False)

    def __unicode__(self):
        return '{}: {}'.format(self.user, self.uuid)
