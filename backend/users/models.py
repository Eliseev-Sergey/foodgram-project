from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.constants import EMAIL_LEN, USER_FIELD_LEN


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_LEN,
        unique=True
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USER_FIELD_LEN,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=USER_FIELD_LEN
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=USER_FIELD_LEN
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscriptions_unique'),
            models.CheckConstraint(
                check=models.Q(user=models.F('author')),
                name='self_subscription_denied')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
