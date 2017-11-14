# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponse
from rest_framework import viewsets

from .models import Todo
from .serializers import TodoSerializer


def ready(_):
    return HttpResponse('OK')


def live(_):
    return HttpResponse('OK')


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    queryset = Todo.objects.all()
