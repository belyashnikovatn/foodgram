import logging
import os
from csv import reader

from django.core.management.base import BaseCommand

from foodgram.settings import CSV_FILES_DIR
from recipes.models import Ingredient, Tag

logging.basicConfig(
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def load(csv_file, model):
    """Загружает файл в модель."""

    with open(os.path.join(CSV_FILES_DIR, csv_file), encoding='utf-8') as rows:
        logging.info(f'Начинаю загружать {csv_file} в {model}')
        try:
            for row in reader(rows):
                # не смогла найти, как вынести поле модели в параметр :(
                model.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1],
                ) if model == Ingredient else model.objects.get_or_create(
                    name=row[0],
                    slug=row[1],
                )
            logging.info(f'Данные {csv_file} успешно загружены')
        except Exception as error:
            logging.error(f'Ошибка {error}! Смотри {row} в {csv_file}')


class Command(BaseCommand):
    help = 'Загружает данные из csv-файлов в models.'

    def handle(self, *args, **options):
        """Загружает ингредиенты и тэги."""
        [load(*item) for item in [
            ('ingredients.csv', Ingredient), ('tags.csv', Tag)]]
