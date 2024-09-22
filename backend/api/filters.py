# import django_filters

# from recipes.models import Ingredient


# class IngredientFilter(django_filters.FilterSet):
#     """Поиск ингредиента для создания в рецепте."""
#     name = django_filters.CharFilter(
#         field_name='name',
#         lookup_expr='istartswith',
#     )

#     class Meta:
#         model = Ingredient
#         fileds = ('name')
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe


User = get_user_model()

class IngredientFilter(filters.FilterSet):
    """Фильтрация ингредиентов по названию."""

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтрация по избранному, автору, списку покупок и тегам."""

    author = filters.ModelChoiceFilter(
        field_name='author',
        label='Автор',
        queryset=User.objects.all(),
    )
