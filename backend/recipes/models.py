from django.db import models
from django.contrib.auth import get_user_model

from foodgram.constants import SLICE_LENGTH
from foodgram.validators import real_time


User = get_user_model()


class Tag(models.Model):
    """Тэг для рецепта"""

    name = models.CharField('Название', unique=True, max_length=32)
    slug = models.SlugField('slug', unique=True, max_length=32)

    class Meta:
        ordering = ('name',)
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:SLICE_LENGTH]


class Ingredient(models.Model):
    """Ингридиент для рецепта"""

    name = models.CharField('Название', unique=True, max_length=128)
    measurement_unit = models.CharField('Единица измерения', max_length=64)

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name[:SLICE_LENGTH]


class Recipe(models.Model):
    """Рецепт"""

    name = models.CharField('Название', max_length=256)
    text = models.TextField('Описание')
    cooking_time = models.IntegerField(
        'Время приготовления (в минутах)',
        validators=(real_time,),
    )
    image = models.ImageField(upload_to='media/recipes')
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тэг(и)',
        through='RecipeTag',
        related_name='recipes',
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент(ы)',
        through='RecipeIngredient',
        related_name='recipes'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} by {self.author}'


class RecipeTag(models.Model):
    """Тэги конкретного рецепта"""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'тэг рецепта'
        verbose_name_plural = 'Тэги рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'На {self.tag} подойдёт {self.recipe[:SLICE_LENGTH]}'


class RecipeIngredient(models.Model):
    """Ингредиенты конкретного рецепта"""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe[:SLICE_LENGTH]}'
