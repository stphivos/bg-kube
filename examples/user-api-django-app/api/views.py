# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework import viewsets

from .serializers import UserSerializer
from .permissions import IsAuthenticatedOrCreateOnly


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
