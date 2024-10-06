import logging
import os
from csv import reader

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILES_DIR
from recipes.models import Ingredient, Tag

User = get_user_model()

logging.basicConfig(
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def load(csv_file, model, *fields):
    """Загружает файл в модель по конкретным полям."""

    if model.objects.first() != model.objects.last():
        logging.info(f'В {model._meta.db_table} уже есть данные.')
        return

    with open(os.path.join(CSV_FILES_DIR, csv_file), encoding='utf-8') as rows:
        logging.info(f'Начинаю загружать {csv_file} в {model._meta.db_table}')
        try:
            for row in reader(rows):
                model.objects.create_user(
                    **dict(zip(fields, row))
                ) if model == User else model.objects.create(
                    **dict(zip(fields, row))
                )
            logging.info(f'Данные {csv_file} успешно загружены')
        except Exception as error:
            logging.error(f'Ошибка {error}! Смотри {row} в {csv_file}')


class Command(BaseCommand):
    help = 'Загружает данные из csv-файлов в models по конкретным полям.'

    def handle(self, *args, **options):
        """Загружает из файлов в модели по полям."""

        models = [
            ('tags.csv', Tag, 'name', 'slug'),
            ('ingredients.csv', Ingredient, 'name', 'measurement_unit'),
            (
                'users.csv', User,
                'username', 'email',
                'first_name', 'last_name',
                'password', 'avatar')
        ]

        [load(*item) for item in models]
