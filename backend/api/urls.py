from django.urls import include, path
from rest_framework import routers

from api.views import (
    TagViewSet
)

v1_router = routers.DefaultRouter()
v1_router.register('tags', TagViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]