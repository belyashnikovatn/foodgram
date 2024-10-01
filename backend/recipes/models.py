from django.contrib.auth import get_user_model
from django.db import models

from foodgram.constants import SLICE_LENGTH
from foodgram.validators import real_amount, real_time

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
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(real_time,),
    )
    image = models.ImageField(
        upload_to='recipes',
        verbose_name='Красивая картинка')
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэг(и)',
        through='RecipeTag',
        related_name='tags'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент(ы)',
        through='RecipeIngredient',
        related_name='ingredients'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} by {self.author}'


class RecipeTag(models.Model):
    """Тэги конкретного рецепта"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт')
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        verbose_name='Тег')

    class Meta:
        ordering = ('recipe', 'tag')
        verbose_name = 'тэг для рецепта'
        verbose_name_plural = 'Тэги для рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]

    def __str__(self):
        return f'На {self.tag} подойдёт {self.recipe}'


class RecipeIngredient(models.Model):
    """Ингредиенты конкретного рецепта"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
        validators=(real_amount,),
    )

    class Meta:
        ordering = ('recipe', 'ingredient')
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'Закидываем {self.ingredient} в {self.recipe}'


class Subscription(models.Model):
    """Подписка пользователя на пользователя"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Пользователь')
    cooker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='Повар')

    class Meta:
        ordering = ('user',)
        verbose_name = 'подипска'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'cooker'],
                name='unique_user_cooker'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан(а) на {self.cooker}'


class FavoriteRecipe(models.Model):
    """Избранные рецепты пользователя"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='liked',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user', 'recipe')
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Рецепт {self.recipe} находится в избранном у {self.user}'


class ShopRecipe(models.Model):
    """Рецепты в списке покупок пользователя"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shops',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopper',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('user', 'recipe')
        verbose_name = 'рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self):
        return f'Рецепт {self.recipe} находится в списке покупок у {self.user}'
