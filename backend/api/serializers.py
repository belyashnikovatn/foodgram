from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from django.contrib.auth import get_user_model

from recipes.models import (
    Ingredient, Recipe,
    Subscription, Tag
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('__all__')


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
