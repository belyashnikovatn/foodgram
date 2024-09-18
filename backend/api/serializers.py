import base64
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile


from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Для расшифровки изображений (рецепт, аватар)."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserPostSerializer(UserCreateSerializer):
    """Для создания пользователя."""

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def to_representation(self, instance):
        return UserPostResultSerializer(instance).data


class UserPostResultSerializer(UserSerializer):
    """Для отображения после создания пользователя."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


class UserGetSerializer(UserSerializer):
    """Для отображения при запросе GET."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar')

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user, subscription=obj).exists()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    current_password = serializers.CharField(required=True, write_only=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'image',
            'name', 'text', 'cooking_time', 'author')


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    users = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = ('user', 'subscription')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscription')
            )
        ]

    def validate(self, data):
        if data['subscription'] == self.context['request'].user:
            raise serializers.ValidationError
        return data
