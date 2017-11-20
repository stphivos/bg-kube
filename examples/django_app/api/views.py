# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import viewsets

from .models import Todo
from .serializers import UserSerializer, TodoSerializer
from .permissions import IsAuthenticatedOrCreateOnly, IsUserOwner


def ready(_):
    return HttpResponse('OK')


def live(_):
    return HttpResponse('OK')


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'patch']
    permission_classes = [IsAuthenticatedOrCreateOnly]

    def get_object(self):
        return self.request.user


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
