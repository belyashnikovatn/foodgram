from csv import reader

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Загружает ингредиенты и тэги."""
        with open(
            'recipes/data/ingredients.csv', 'r',
            encoding='UTF-8'
        ) as ingredients:
            for row in reader(ingredients):
                if len(row) == 2:
                    Ingredient.objects.get_or_create(
                        name=row[0], measurement_unit=row[1],
                    )
        with open(
            'recipes/data/tags.csv', 'r',
            encoding='UTF-8'
        ) as tags:
            for row in reader(tags):
                if len(row) == 2:
                    Tag.objects.get_or_create(
                        name=row[0], slug=row[1],
                    )
        print('Данные загружены!')
