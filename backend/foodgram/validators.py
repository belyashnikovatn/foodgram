from django.core.exceptions import ValidationError


def real_time(value):
    if value < 1:
        raise ValidationError(
            'Укажите верное время -- больше 1 минуты.'
        )
