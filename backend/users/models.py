from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """ Пользовательская модель CustomUser."""
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        null=False
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=150,
        null=True,
        blank=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email


class Subscriptions(models.Model):
    """ Модель подписки на публикации авторов рецептов."""
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='publisher',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
