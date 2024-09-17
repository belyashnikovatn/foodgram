# Generated by Django 3.2.3 on 2024-09-16 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20240916_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredient',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='tag',
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='recipes.RecipeIngredient', to='recipes.Ingredient', verbose_name='Ингредиент(ы)'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(through='recipes.RecipeTag', to='recipes.Tag', verbose_name='Тэг(и)'),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=1, verbose_name='Количество в рецепте'),
            preserve_default=False,
        ),
    ]