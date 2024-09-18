from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination

from djoser.views import UserViewSet as UVS
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializers import (
    IngredientSerializer, RecipeSerializer,
    SetPasswordSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserPostSerializer, UserGetSerializer,
)
from recipes.models import (
    Ingredient, Recipe,
    Subscription, Tag
)

User = get_user_model()


class UserViewSet(UVS):
    queryset = User.objects.all()
    # serializer_class = UserGetSerializer
    pagination_class = LimitOffsetPagination
    

    # @action(detail=True, methods=['post'])
    # def set_password(self, request, pk=None):
    #     user = self.get_object()
    #     serializer = SetPasswordSerializer(data=request.data)
    #     if serializer.is_valid():
    #         user.set_password(serializer.validated_data['password'])
    #         user.save()
    #         return Response({'status': 'password set'})
    #     else:
    #         return Response(serializer.errors,
    #                         status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=('get',), permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
