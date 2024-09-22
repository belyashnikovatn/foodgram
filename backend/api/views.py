from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from api.permissions import OwnerOnly

from djoser.views import UserViewSet as UVS
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.serializers import (
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
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
from api.filters import IngredientFilter, RecipeFilter

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
    # filterset_fields = ('name',)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, OwnerOnly)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeGetSerializer
        if self.action == 'retrieve':
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Action для избранного рецепта."""
        return Response({'message': f'That MAIN recipe action for {self}.'})

    @favorite.mapping.post
    def add_into_fav(self, request, pk):
        """Добавить рецепт в избранное."""
        return Response({'message': f'Add recipe into {pk} favs.'})

    @favorite.mapping.delete
    def del_from_fav(self, request, pk):
        """Удалить рецепт из избранного."""
        return Response({'message': f'Del recipe from {pk} favs.'})

    @action(detail=True, permission_classes=(AllowAny,), url_path='get-link')
    def get_link(self, request, pk):
        """Получить короткую ссылку на рецепт."""
        return Response({'message': f'Get your link to {pk} res.'})

    """Вот это место точно можно улушчить, но это потом"""

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Action для списка покупок."""
        return Response({'message': f'That MAIN shopping_cart action for {self}.'})

    @shopping_cart.mapping.post
    def add_into_cart(self, request, pk):
        """Добавить рецепт в избранное."""
        return Response({'message': f'Add recipe into {pk} shopping_cart.'})

    @shopping_cart.mapping.delete
    def del_from_cart(self, request, pk):
        """Удалить рецепт из избранного."""
        return Response({'message': f'Del recipe from {pk} shopping_cart.'})

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        return Response({'message': 'download_shopping_cart.'})
