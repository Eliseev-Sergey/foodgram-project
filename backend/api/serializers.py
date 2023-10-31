from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer
from users.models import CustomUser, Subscriptions

class CustomUserCreateSerializer(UserCreateSerializer):
    """Cериализатор создает пользователя."""
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password')


class CustomUserSerializer(UserSerializer):
    """Cериализатор пользователя. Добавляет ключ is_subscribed в
    сериализованное представление пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        follow = self.context["follow"]
        if str(user) != "AnonymousUser":
            if follow.filter(user=user, author=obj):
                return True
            return False
        return None
            