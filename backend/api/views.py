from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404


from djoser.views import UserViewSet as UVS
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserGetSerializer,
)
from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag
)

User = get_user_model()


class UserViewSet(UVS, viewsets.ViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Показать профиль текущего пользователя."""
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path=r'me/avatar')
    def avatar(self, request):
        """Action для аватара."""
        return Response({'message': f'That action MAIN for {request.user}.'})

    @avatar.mapping.patch
    def set_avatar(self, request):
        """Добавить аватар текущего пользователя."""
        return Response({'message': f'That action set avatar for {request.user}.'})

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удалить аватар текущего пользователя."""
        return Response({'message': f'That action delete avatar for {request.user}.'})

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Список подписок."""
        user = get_object_or_404(User, pk=request.user.id)
        subscriptions = user.following.all()
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        """Action для подписки/отписки."""

    @subscribe.mapping.post
    def create_subs(self, request, id=None):
        """Подписаться на пользователя."""
        request.data['user'] = get_object_or_404(User, pk=request.user.id)
        request.data['cooker'] = get_object_or_404(User, pk=id)
        serializer = SubscriptionSerializer(data=request.data,
                                            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subs(self, request, id=None):
        """Отписаться от пользователя."""
        user = get_object_or_404(User, pk=request.user.id)
        cooker = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(user=user, cooker=cooker)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    @action(detail=True,)
    def favorite(self, request, id=None):
        """Action для избранного рецепта."""
        
        return Response({'message': f'That MAIN recipe action for {self}.'})

    @favorite.mapping.post
    def add_into_fav(self, request, id=None):
        """Добавить рецепт в избранное."""
        return Response({'message': f'Add recipe {self} into favs.'})

    @favorite.mapping.delete
    def del_from_fav(self, request, id=None):
        """Удалить рецепт из избранного."""
        return Response({'message': f'Del recipe {self} from favs.'})
