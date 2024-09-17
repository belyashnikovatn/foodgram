from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from foodgram.constants import USERNAME_REGEX


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    email = models.EmailField(
        'Адрес эл.почты',
        unique=True,
        max_length=254
    )
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        max_length=150,
        validators=[RegexValidator(
            regex=USERNAME_REGEX,
            message='Unacceptable symbol'
        )]
    )
    first_name = models.CharField(
        'Имя',
        max_length=150
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
