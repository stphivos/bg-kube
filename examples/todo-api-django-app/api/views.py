# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.http import HttpResponse
from rest_framework import viewsets

from .models import Todo
from .serializers import TodoSerializer
from .permissions import IsUserOwner


def ready(_):
    return HttpResponse('OK')


def live(_):
    return HttpResponse('OK')


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    queryset = Todo.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [IsUserOwner]

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user

        return super(TodoViewSet, self).perform_create(serializer)
