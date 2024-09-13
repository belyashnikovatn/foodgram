from django.shortcuts import render
from rest_framework import viewsets

from api.serializers import IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
