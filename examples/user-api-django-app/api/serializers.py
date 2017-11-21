# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    uuid = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def get_uuid(self, obj):
        return obj.profile.uuid

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'uuid')
        read_only_fields = ('id',)
