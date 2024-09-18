from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model


from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag
)

User = get_user_model()


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

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, subscription=obj).exists()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    current_password = serializers.CharField(required=True, write_only=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


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
