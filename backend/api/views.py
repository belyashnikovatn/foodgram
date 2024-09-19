from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, QuerySet


from djoser.views import UserViewSet as UVS
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

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


class UserViewSet(UVS, viewsets.ViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=('get', 'post',))
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            return Response({'message': 'You pick post subscribe'})
        elif request.method == 'GET':
            return Response({'message': 'You pick GET'})


    # @action(detail=True, permission_classes=(IsAuthenticated,))
    # def subscribe(self, request):
    #     """"""

    # @subscribe.mapping.post
    # def create_subscribe(self, request, pk):
    #     serializer = self.get_serializer(
    #         data=request.data,
    #         context={'request': request, 'id': pk}
    #         )
    #     serializer.is_valid(raise_exception=True)
    #     response_data = serializer.save(id=pk)
    #     return Response(
    #         {'message': 'Подписка успешно создана',
    #             'data': response_data},
    #         status=status.HTTP_201_CREATED
    #     )

    # @subscribe.mapping.delete
    # def delete_subscribe(self, request, id):
    #     return self._delete_relation(Q(subscription__id=id))



    # @me.mapping.avatar
    # def avatar(self, request):
    #     serializer = UserPostSerializer(
    #         instance=request.user,
    #         data=request.data,
    #         partial=True
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(role=request.user.role)
    #     return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)

    @action(detail=False, url_path='branch')
    def branch(self, request):
        tags = Tag.objects.filter(name='завтрак')
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)


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


class SubscriptionViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return user.subscriptions.all()
