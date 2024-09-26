from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from recipes.models import Ingredient, Recipe, Tag


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

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ('author', 'is_in_shopping_cart', 'is_favorited')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopper__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(followers__user=user)
        return queryset
