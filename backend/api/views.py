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

    # @action(detail=True, methods=('get', 'post',))
    # def subscribe(self, request, id=None):
    #     if request.method == 'POST':
    #         return Response({'message': f'Custom POST action executed for instance {id}.'})
    #     elif request.method == 'GET':
    #         return Response({'message': f'You pick GET for {id}'})

    @action(detail=True)
    def subscribe(self, request, id=None):
        """"""
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

    @subscribe.mapping.post
    def create_subs(self, request, id=None):
        # return Response({'message': 'Получены данные', 'data': request.data})
        return Response({'message': f'Custom POST action executed for instance {request.user} wnats {id}.'})

    # @subscribe.mapping.get
    # def get_subs(self, request, id=None):
    #     return Response({'message': f'That would be simple get  {id}.'})

    @subscribe.mapping.delete
    def delete_subs(self, request, id=None):
        return Response({'message': f'That would be unscribe for {id}.'})

# if request.method == 'POST':
#         serializer = CatSerializer(data=request.data, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     # В случае GET-запроса возвращаем список всех котиков
#     cats = Cat.objects.all()
#     serializer = CatSerializer(cats, many=True)
#     return Response(serializer.data) 

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

    # @action(detail=False, url_path='branch')
    # def branch(self, request):
    #     tags = Tag.objects.filter(name='завтрак')
    #     serializer = self.get_serializer(tags, many=True)
    #     return Response(serializer.data)


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
