from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import serializers
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.serializers import CustomUserSerializer
from users.models import CustomUser

class CustomUserViewSet(UserViewSet):
    """."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = IsAuthenticated

    def subscribed(self, obj):
        pass