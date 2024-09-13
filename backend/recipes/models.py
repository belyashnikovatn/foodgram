from django.db import models

from recipes.constants import SLICE_LENGTH


class Tag(models.Model):
    """Тэг для рецепта"""

    name = models.CharField('Название', unique=True, max_length=32)
    slug = models.SlugField('slug', unique=True, max_length=32)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:SLICE_LENGTH]


class Ingredient(models.Model):
    """Ингридиент для рецепта"""

    name = models.CharField('Название', unique=True, max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:SLICE_LENGTH]
