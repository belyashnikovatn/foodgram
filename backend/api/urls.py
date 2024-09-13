from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientViewSet,
    TagViewSet
)

v1_router = routers.DefaultRouter()
v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
]
