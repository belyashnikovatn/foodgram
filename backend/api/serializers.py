import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram.constants import (
    MAX_AMOUNT,
    MAX_COOKING,
    MIN_AMOUNT,
    MIN_COOKING
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShopRecipe,
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
    """
    ТОЛЬКО для создания пользователя.
    Унаследован от djoser, чтобы взять пароль, токен итд.
    """

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'password')


class UserGetSerializer(UserSerializer):
    """Для изменения и отображения при запросе GET."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar')

    def validate(self, data):
        """Фото не пустое?"""
        if request := self.context.get('request'):
            if request.method == 'PUT' and not data:
                raise serializers.ValidationError('Выберите фото')
        return data

    def get_is_subscribed(self, obj):
        """Текущий юзер подписан?"""
        if request := self.context.get('request'):
            if request.user.is_anonymous:
                return False
            return request.user.following.filter(cooker=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Для тегов"""
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    """Для инргедиентов"""
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Для просмотра рецепта"""
    author = UserGetSerializer()
    tags = TagSerializer(
        many=True,
    )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )
        return ingredients

    def get_is_recipe(self, obj, model):
        if request := self.context.get('request'):
            user = request.user
            if user.is_anonymous:
                return False
            # фильтр используется, потому что на входе функции может
            # быть любая модель, а значит related_name могут быть разными
            return model.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        return self.get_is_recipe(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_recipe(obj, ShopRecipe)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиент в рецепте -- используется при создании"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        write_only=True,
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    """Для создания рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_null=False,
        allow_empty=False,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        allow_null=False,
        allow_empty=False,)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True, allow_null=False)
    name = serializers.CharField(required=True, max_length=256)
    cooking_time = serializers.IntegerField(
        max_value=MAX_COOKING, min_value=MIN_COOKING)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
            'author')

    def validate(self, data):
        if 'tags' not in data:
            raise serializers.ValidationError(
                'Рецепт не может быть без тегов')
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                'Рецепт не может быть без ингредиентов')
        return data

    def validate_ingredients(self, data):
        ingredients_list = [item['id'].id for item in data]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError('Повтор ингредиентов')
        get_list_or_404(Ingredient, id__in=ingredients_list)
        return data

    def validate_tags(self, data):
        tags_list = [item.id for item in data]
        if len(tags_list) != len(set(tags_list)):
            raise serializers.ValidationError('Повтор тегов')
        get_list_or_404(Tag, id__in=tags_list)
        return data

    def add_tags_ingredients(self, recipe, tags, ingredients):
        """Добавляет теги и ингредиенты в рецепт"""
        RecipeTag.objects.bulk_create([
            RecipeTag(recipe=recipe, tag=tag) for tag in tags
        ])
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=dict(ingredient).get('id'),
                amount=dict(ingredient).get('amount')
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        recipe.tags.clear()
        recipe.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        self.add_tags_ingredients(recipe, tags, ingredients)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        return RecipeGetSerializer(instance).data


class RecipeListSerializer(serializers.ModelSerializer):
    """Мини-рецепт для отображения"""
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserRecepieSerializer(serializers.Serializer):
    """
    Общий сериализатор для обработки рецептов:
    доблавение/удаление в избранное/лист покупок.
    """

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context.get('recipe_pk')
        # действие: удалить или добавить
        action = self.context.get('action')
        # целевая модель добавления
        model = self.context.get('model')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not recipe:
            raise serializers.ValidationError('Такого рецепта нет')
        # фильтр используется, потому что на входе функции может
        # быть любая модель, а значит related_name могут быть разными
        userrecipe = model.objects.filter(user=user, recipe=recipe)
        if action == 'del':
            if not userrecipe:
                raise serializers.ValidationError('Нечего удалять')
        if action == 'add':
            if userrecipe:
                raise serializers.ValidationError('Такое уже есть')
        return data

    def create(self, validated_data):
        model = self.context.get('model')
        recipe = get_object_or_404(Recipe, pk=validated_data.get('pk'))
        model.objects.create(
            user=self.context['request'].user,
            recipe=recipe)
        return RecipeListSerializer(recipe)


class SubscriptionSerializer(serializers.Serializer):
    """Для валидации и создания подписки"""

    def validate(self, data):
        user = self.context['request'].user
        subs_id = self.context.get('user_pk')
        action = self.context.get('action')

        subs = get_object_or_404(User, pk=subs_id)
        if not subs:
            raise serializers.ValidationError('А на кого подписываемся?')
        if user == subs:
            raise serializers.ValidationError('На себя нельзя подписаться')

        subscription = user.following.filter(cooker=subs)
        if action == 'delete_subs':
            if not subscription:
                raise serializers.ValidationError('Такой подписки нет')
        if action == 'create_subs':
            if subscription:
                raise serializers.ValidationError('Подписка уже есть')
        return data

    def create(self, validated_data):
        limit_param = self.context.get('limit_param')
        subs = get_object_or_404(User, pk=validated_data.get('pk'))
        Subscription.objects.create(
            user=self.context['request'].user,
            cooker=subs)
        return UserSubscriptionsSerializer(
            subs,
            context={'limit_param': limit_param})


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Для отображения подписки: count_recepie и recipe"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
            'recipes_count',
            'recipes',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        if limit_param := self.context.get('limit_param'):
            recipes = recipes[:int(limit_param)]
        serializer = RecipeListSerializer(recipes, many=True, read_only=True)
        return serializer.data
