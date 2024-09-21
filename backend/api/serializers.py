import base64
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile


from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
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
            user=user, cooker=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    cooker = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        """"""
        model = Subscription
        fields = ('user', 'cooker')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'cooker')
            )
        ]

    def validate(self, data):
        if data['cooker'] == self.context['request'].user:
            raise serializers.ValidationError('You cannot subscribe yourself')
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    author = UserGetSerializer()
    tags = TagSerializer(
        many=True, required=True,
        allow_null=False, allow_empty=False
    )
    ingredients = IngredientSerializer(
        many=True, required=True,
        allow_null=False, allow_empty=False)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
            'author')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            product = dict(ingredient)['id']
            amount = dict(ingredient)['amount']
            RecipeIngredient.objects.create(recipe=recipe, ingredient=product, amount=amount)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        old_tags = recipe.tags.all()
        new_tags = validated_data.pop('tags')
        to_del = set(old_tags) - set(new_tags)
        RecipeTag.objects.filter(recipe=recipe, tag__in=to_del).delete()
        to_add = set(new_tags) - set(old_tags)
        RecipeTag.objects.bulk_create([
            RecipeTag(recipe=recipe, tag=tag) for tag in to_add
        ])
        # print(type(to_del), to_del)
        print('00000000000000000000')
        # to_del = set(old_ingredients) - set(new_ingredients)
        # to_add = set(new_ingredients) - set(old_ingredients)

        old_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        old_ingredients_products = [RecipeIngredient.ingredient_id for RecipeIngredient in old_ingredients]
        # print(old_ingredients_products)
        new_ingredients = validated_data.pop('ingredients')
        new_ingredients_ids = [dict(item)['id'].id for item in new_ingredients]

        # Удаляем те ингредиенты, которых нет в новых данных.
        for item in old_ingredients:
            if item.ingredient.id not in new_ingredients_ids:
                print(f'this is gona del {item.ingredient}')
                RecipeIngredient.objects.filter(ingredient=item.ingredient).delete()
        # Добавляем те ингредиенты, которых нет в рецепте.
        # Обновляем количество тех, которые есть в рецепте.
        for item in new_ingredients:
            product, amount = dict(item)['id'], dict(item)['amount']
            if product.id not in old_ingredients_products:
                RecipeIngredient.objects.create(recipe=recipe, ingredient=product, amount=amount)
            else:
                RecipeIngredient.objects.filter(recipe=recipe, ingredient=product).update(amount=amount)
        return recipe

    def to_representation(self, instance):
        return RecipeGetSerializer(instance).data
