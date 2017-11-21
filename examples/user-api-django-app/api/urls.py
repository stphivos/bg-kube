# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers

from . import views
from .routers import SingleRecordRouter

router = routers.DefaultRouter()

sr_router = SingleRecordRouter()
sr_router.register(r'user', views.UserViewSet, base_name='user')

urlpatterns = [
    url(r'^ready', views.ready),
    url(r'^live', views.live),
    url(r'^', include(router.urls)),
    url(r'^', include(sr_router.urls)),
]
