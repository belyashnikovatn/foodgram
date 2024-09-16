from django.shortcuts import render
from django.contrib.auth import get_user_model

from djoser import views as djoser_views
from rest_framework import mixins, viewsets

from api.serializers import (
    IngredientSerializer, RecipeSerializer,
    SubscriptionSerializer, TagSerializer,
    UserSerializer
)
from recipes.models import (
    Ingredient, Recipe,
    Subscription, Tag
)
from users.models import User


class UserViewSet(djoser_views.UserViewSet):
    query_set = User.objects.all()
    serializer_class = UserSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class SubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
