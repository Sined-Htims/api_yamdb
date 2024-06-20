from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users import validators


class CustomUser(AbstractUser):
    """Кастомная модель пользователя"""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin')
    )

    username = models.CharField(
        max_length=settings.USERNAME_MAX_LENGTH, unique=True,
        validators=[validators.username_validator, validators.username_not_me],
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        verbose_name='Email', max_length=settings.EMAIL_MAX_LENGTH, unique=True
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES, default=USER
    )
    is_moderator = models.BooleanField(verbose_name='Moderator', default=False)
    bio = models.TextField(verbose_name='О себе', blank=True)

    @property
    def is_admin(self):
        return (self.is_staff or self.is_superuser or self.role == self.ADMIN)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
