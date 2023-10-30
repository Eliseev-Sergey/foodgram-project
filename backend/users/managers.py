from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """ Пользовательский Manager, который  использует email в качестве
    уникального идентификатора для аутентификации вместо username.
    """
    def create_user(self, email, password, **extra_fields):
        """ Создать и сохранить пользователя по email и password."""
        if not email:
            raise ValueError('Укажите адрес электронной почты!')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """ Создать и сохранить superuser по email и password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)
