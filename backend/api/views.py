from django.shortcuts import render
from rest_framework import viewsets

from api.serializers import TagSerializer
from recipes.models import Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
