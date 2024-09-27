import short_url
from django.conf import settings
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
    # AvatarSerializer,
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeGetSerializer,
    RecipeListSerializer,
    RecipePostSerializer,
    ShopRecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserGetSerializer,
    UserPostSerializer,
    UserSubscriptionsSerializer,
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    ShopRecipe,
    Subscription,
    Tag
)
from api.filters import IngredientFilter, RecipeFilter
from django.shortcuts import redirect


from rest_framework.pagination import LimitOffsetPagination

User = get_user_model()


class RecipeLimitPage(LimitOffsetPagination):
    limit_query_param = 'recipes_limit'





def redirect_view(request, s):
    pk = short_url.decode_url(s)
    return redirect(f'/api/recipes/{pk}')


class UserViewSet(UVS, viewsets.ViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Показать профиль текущего пользователя."""
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path=r'me/avatar', permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        """Action для аватара."""
        return Response({'message': f'That action MAIN for {request.user}.'})

    @avatar.mapping.put
    def set_avatar(self, request):
        """Добавить аватар текущего пользователя."""
        user = get_object_or_404(User, pk=request.user.id)
        #  передаём контекст для проверки метода
        serializer = UserGetSerializer(
            user, data=request.data, partial=True,
            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'avatar': serializer.data['avatar']})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удалить аватар текущего пользователя."""
        User.objects.filter(pk=request.user.id).update(avatar=None)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Список подписок."""
        user = get_object_or_404(User, pk=request.user.id)
        users = [user.cooker for user in user.following.all()]
        limit_param = request.query_params.get('recipes_limit')
        paginated_queryset = self.paginate_queryset(users)
        serializer = UserSubscriptionsSerializer(
            paginated_queryset,
            # users,
            context={
                'request': request,
                'method': request.method,
                'limit_param': limit_param},
            many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Action для подписки/отписки."""

    @subscribe.mapping.post
    def create_subs(self, request, id):
        """Подписаться на пользователя."""
        limit_param = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            data=request.data,
            context={
                'request': request,
                'user_pk': id,
                'limit_param': limit_param,
                'action': 'create_subs'})
        if serializer.is_valid():
            subs = serializer.save(pk=id)
            return Response(subs.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subs(self, request, id):
        """Отписаться от пользователя."""
        # limit_param = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            data=request.data,
            context={
                'request': request,
                'user_pk': id,
                # 'limit_param': limit_param,
                'action': 'delete_subs'})
        if serializer.is_valid():
            get_object_or_404(
                Subscription,
                user=self.request.user,
                cooker=get_object_or_404(User, pk=id)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    # pagination_class = PageLimitPagination
    # pagination_class = RecipeLimitPage
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
        serializer = FavoriteRecipeSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add_into_fav'})
        if serializer.is_valid():
            short_recipe = serializer.save(pk=pk)
            return Response(short_recipe.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def del_from_fav(self, request, pk):
        """Удалить рецепт из избранного."""
        serializer = FavoriteRecipeSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'del_from_fav'})
        if serializer.is_valid():
            get_object_or_404(
                FavoriteRecipe,
                user=self.request.user,
                recipe=get_object_or_404(Recipe, pk=pk)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, permission_classes=(AllowAny,), url_path='get-link')
    def get_link(self, request, pk):
        """Получить короткую ссылку на рецепт."""
        # url = short_url.encode_url(int(pk))
        url = 'https://{}/s/{}'.format(
            settings.ALLOWED_HOSTS[-1],
            short_url.encode_url(int(pk))
        )
        print(request)

        return Response({'short-link': url})

    """Вот это место точно можно улушчить, но это потом"""

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Action для списка покупок."""
        return Response({'message': f'That MAIN shopping_cart action for {self}.'})

    @shopping_cart.mapping.post
    def add_into_cart(self, request, pk):
        """Добавить рецепт в список покупок."""
        serializer = ShopRecipeSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add_into_cart'})
        if serializer.is_valid():
            short_recipe = serializer.save(pk=pk)
            # return Response({'message': 'Its all goor Gonna ADD.'})
            return Response(short_recipe.data, status=status.HTTP_201_CREATED)
            # return Response(, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def del_from_cart(self, request, pk):
        """Удалить рецепт из списка покупок."""
        serializer = ShopRecipeSerializer(
            data=request.data,
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'del_from_cart'})
        if serializer.is_valid():
            get_object_or_404(
                ShopRecipe,
                user=self.request.user,
                recipe=get_object_or_404(Recipe, pk=pk)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        return Response({'message': 'download_shopping_cart.'})
