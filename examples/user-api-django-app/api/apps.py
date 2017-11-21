# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        import api.signals  # noqa: F401
