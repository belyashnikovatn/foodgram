from django.core.exceptions import ValidationError

from foodgram.constants import (
    MAX_AMOUNT,
    MIN_AMOUNT,
    MAX_COOKING,
    MIN_COOKING,
)


def real_time(value):
    if not MIN_COOKING < value < MAX_COOKING:
        raise ValidationError(
            'Укажите время в диапазоне от 1 минуты до 32 000 минут.'
        )


def real_amount(value):
    if not MIN_AMOUNT < value < MAX_AMOUNT:
        raise ValidationError(
            'Укажите количество в диапазоне от 1 до 32 000.'
        )
