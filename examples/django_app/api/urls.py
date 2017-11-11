# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'todos', views.TodoViewSet, base_name='todos')

urlpatterns = [
    url(r'^', include(router.urls)),
]
