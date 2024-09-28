import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

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
            if request.method == 'PUT' and len(data) == 0:
                raise serializers.ValidationError('Выберите фото')
        return data

    def get_is_subscribed(self, obj):
        """Текущий юзер подписан?"""
        if request := self.context.get('request'):
            if request.user.is_anonymous:
                return False
            return Subscription.objects.filter(
                user=request.user, cooker=obj).exists()
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return ShopRecipe.objects.filter(
            user=user, recipe=obj).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Ингредиент в рецепте -- используется при создании"""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True, min_value=1)

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

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
            'author')

    def validate(self, data):
        if 'tags' not in data or 'ingredients' not in data:
            raise serializers.ValidationError(
                'Рецепт не может быть без тегов или ингредиентов')
        return data

    def validate_ingredients(self, data):
        # if not data:
        #     raise serializers.ValidationError('Ай яйяйяй!')
        ingredients_list = [dict(item)['id'].id for item in data]
        ingredients_set = set(ingredients_list)
        if len(ingredients_list) != len(ingredients_set):
            raise serializers.ValidationError('Ать по рукам!')
        return data

    def validate_tags(self, data):
        # if not data:
        #     raise serializers.ValidationError('Ай яйяйяй!')
        tags_list = [item.id for item in data]
        tags_set = set(tags_list)
        if len(tags_list) != len(tags_set):
            raise serializers.ValidationError('Ать по рукам!')
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            product = dict(ingredient)['id']
            amount = dict(ingredient)['amount']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=product,
                amount=amount)
        return recipe

    def update(self, instance, validated_data):
        recipe = instance

        # Работа с тегами: удалить/добавить
        old_tags = recipe.tags.all()
        new_tags = validated_data.pop('tags')
        to_del = set(old_tags) - set(new_tags)
        # Удаляем те теги, которых нет в новых данных
        RecipeTag.objects.filter(recipe=recipe, tag__in=to_del).delete()
        to_add = set(new_tags) - set(old_tags)
        # Добавляем те теги, которых нет в рецепте
        RecipeTag.objects.bulk_create([
            RecipeTag(recipe=recipe, tag=tag) for tag in to_add
        ])

        # Работа с инредиентами: удалить, добавить, изменить
        old_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        old_ingredients_products = [
            recipeingredient.ingredient_id for recipeingredient
            in old_ingredients]
        new_ingredients = validated_data.pop('ingredients')
        new_ingredients_ids = [dict(item)['id'].id for item in new_ingredients]

        # Удаляем те ингредиенты, которых нет в новых данных.
        for item in old_ingredients:
            if item.ingredient.id not in new_ingredients_ids:
                RecipeIngredient.objects.filter(
                    ingredient=item.ingredient).delete()
        # Добавляем те ингредиенты, которых нет в рецепте.
        # Обновляем количество тех, которые есть в рецепте.
        for item in new_ingredients:
            product, amount = dict(item)['id'], dict(item)['amount']
            if product.id not in old_ingredients_products:
                RecipeIngredient.objects.create(
                    recipe=recipe, ingredient=product, amount=amount)
            else:
                RecipeIngredient.objects.filter(
                    recipe=recipe, ingredient=product).update(amount=amount)
        Recipe.objects.filter(id=recipe.id).update(**validated_data)
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


class FavoriteRecipeSerializer(serializers.Serializer):
    """ВОТ ЭТО ВОТ Я ЕЩЁ МОГУ ПЕРЕДЕЛАТЬ"""

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context['recipe_pk']
        action = self.context['action']
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not recipe:
            raise serializers.ValidationError('Ай яйяйяй!')
        faverecipe = FavoriteRecipe.objects.filter(user=user, recipe=recipe)
        if action == 'del_from_fav':
            if not faverecipe:
                raise serializers.ValidationError('Thete is noy that sjop ')
        if action == 'add_into_fav':
            if faverecipe:
                raise serializers.ValidationError('Doulble trule ')
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data['pk'])
        FavoriteRecipe.objects.create(
            user=self.context['request'].user,
            recipe=recipe)
        return RecipeListSerializer(recipe)


class ShopRecipeSerializer(serializers.Serializer):
    """И ОБЪЕДИНИТЬ ВОТ С ЭТИМ"""

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = self.context['recipe_pk']
        action = self.context['action']
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not recipe:
            raise serializers.ValidationError('Ай яйяйяй!')
        shoprecipe = ShopRecipe.objects.filter(user=user, recipe=recipe)
        if action == 'del_from_cart':
            if not shoprecipe:
                raise serializers.ValidationError('Thete is noy that sjop ')
        if action == 'add_into_cart':
            if shoprecipe:
                raise serializers.ValidationError('Doulble trule ')
        return data

    def create(self, validated_data):
        recipe = get_object_or_404(Recipe, pk=validated_data.get('pk'))
        ShopRecipe.objects.create(
            user=self.context['request'].user,
            recipe=recipe)
        return RecipeListSerializer(recipe)


class SubscriptionSerializer(serializers.Serializer):
    """Для валидации и создания подписки"""

    def validate(self, data):
        user = self.context.get('request').user
        subs_id = self.context.get('user_pk')
        action = self.context.get('action')

        subs = get_object_or_404(User, pk=subs_id)
        if not subs:
            raise serializers.ValidationError('А на кого подписываемся?')
        if user == subs:
            raise serializers.ValidationError('На себя нельзя подписаться')

        subscription = Subscription.objects.filter(user=user, cooker=subs)
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
            user=self.context.get('request').user,
            cooker=subs)
        return UserSubscriptionsSerializer(
            subs,
            context={'limit_param': limit_param})


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Для отображения подписки: count_recepie и recipe"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        return True

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        if limit_param := self.context.get('limit_param'):
            recipes = recipes[:int(limit_param)]
        serializer = RecipeListSerializer(recipes, many=True, read_only=True)
        return serializer.data
