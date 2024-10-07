import short_url

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as UVS
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,)
                                        # IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import LimitPageNumberPaginator
from api.permissions import OwnerOnly
from api.serializers import (
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserGetSerializer,
    UserRecepieSerializer,
    UserSubscriptionsSerializer,
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShopRecipe,
    Subscription,
    Tag
)

User = get_user_model()


def redirect_view(request, s):
    """Redirect для короткой ссылки"""
    pk = short_url.decode_url(s)
    return redirect(f'/api/recipes/{pk}')


class UserViewSet(UVS):
    """
    Вьюсет для работы с пользователем:
    регистрация, изменение, смена пароля -- djoser.
    Дполнительно: профиль, смена аватара, список подписок,
    создание/удаление подписки
    """
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPaginator

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Показать профиль текущего пользователя."""
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path=r'me/avatar',
            permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        """Action для аватара."""

    @avatar.mapping.put
    def set_avatar(self, request):
        """Добавить аватар текущего пользователя."""
        user = get_object_or_404(User, pk=request.user.id)
        #  передаём контекст для проверки метода
        serializer = UserGetSerializer(
            user, data=request.data, partial=True,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': serializer.data.get('avatar')})

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удалить аватар текущего пользователя."""
        User.objects.filter(pk=request.user.id).update(avatar=None)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Список подписок."""
        users = User.objects.filter(followers__user=request.user)
        limit_param = request.query_params.get('recipes_limit')
        paginated_queryset = self.paginate_queryset(users)
        serializer = UserSubscriptionsSerializer(
            paginated_queryset,
            # передаём контекст для лимита рецептов
            context={
                'limit_param': limit_param},
            many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Action для подписки/отписки."""

    @subscribe.mapping.post
    def create_subs(self, request, id):
        """Подписаться на пользователя."""
        limit_param = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            data=request.data,
            # передаём контекст для валидации
            context={
                'request': request,
                'user_pk': id,
                'limit_param': limit_param,
                'action': 'create_subs'})
        serializer.is_valid(raise_exception=True)
        subs = serializer.save(pk=id)
        return Response(subs.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subs(self, request, id):
        """Отписаться от пользователя."""
        serializer = SubscriptionSerializer(
            data=request.data,
            # передаём контекст для валидации
            context={
                'request': request,
                'user_pk': id,
                'action': 'delete_subs'})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            Subscription,
            user=self.request.user,
            cooker=get_object_or_404(User, pk=id)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов: все CRUD операции,
    добавить/удалить в избранное/список покупок,
    получить короткую ссылку,
    скачать список покупок.
    """
    queryset = Recipe.objects.all()
    # permission_classes = (IsAuthenticatedOrReadOnly, OwnerOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPaginator

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_link'):
            return (AllowAny(),)
        return (IsAuthenticated(), OwnerOnly())

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Action для избранного рецепта."""

    @favorite.mapping.post
    def add_into_fav(self, request, pk):
        """Добавить рецепт в избранное."""
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передаём контекст для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add',
                'model': FavoriteRecipe})
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def del_from_fav(self, request, pk):
        """Удалить рецепт из избранного."""
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передаём контекст для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'del',
                'model': FavoriteRecipe})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            FavoriteRecipe,
            user=self.request.user,
            recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=(AllowAny,), url_path='get-link')
    def get_link(self, request, pk):
        """Получить короткую ссылку на рецепт."""
        url = 'https://{}/s/{}'.format(
            settings.ALLOWED_HOSTS[0],
            short_url.encode_url(int(pk))
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Action для списка покупок."""

    @shopping_cart.mapping.post
    def add_into_cart(self, request, pk):
        """Добавить рецепт в список покупок."""
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передаём контекст для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add',
                'model': ShopRecipe})
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def del_from_cart(self, request, pk):
        """Удалить рецепт из списка покупок."""
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передаём контекст для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'del',
                'model': ShopRecipe})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            ShopRecipe,
            user=self.request.user,
            recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        user = request.user
        if user.is_anonymous:
            return Response({'message': 'анониму анонимный список'})
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=user.shops.values('id'))
        ingredients = {}
        for recipe_ingredient in recipe_ingredients:
            ingredients.setdefault(
                recipe_ingredient.ingredient, []
            ).append(recipe_ingredient.amount)
        text, count = '', 0
        for item in ingredients:
            count += 1
            text += (
                f'{count}. {item.name} - '
                f'{sum(ingredients[item])} '
                f'{item.measurement_unit} \n')
        response = HttpResponse(text, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = 'attachment; filename="shops.txt"'
        return response
