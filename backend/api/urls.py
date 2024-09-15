from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    SubscriptionViewSet,
    TagViewSet,
)

v1_router = routers.DefaultRouter()
v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register(
    r'subscriptions',
    SubscriptionViewSet,
    basename='subscriptions')

urlpatterns = [
    path('', include(v1_router.urls)),
]
