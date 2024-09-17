from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
import re
from django.core.exceptions import ValidationError


from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag
)

User = get_user_model()


class UserPostSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def to_representation(self, instance):
        return UserGetSerializer(instance).data


class UserGetSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name')


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
