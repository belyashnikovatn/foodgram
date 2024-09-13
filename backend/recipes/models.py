from django.db import models

from recipes.constants import MODELS_NAME_LENGTH, SLICE_LENGTH


class Tag(models.Model):
    """Тэг для рецепта"""

    name = models.CharField('Название', max_length=MODELS_NAME_LENGTH)
    slug = models.SlugField('slug', unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:SLICE_LENGTH]
