from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status, validators

from recipes.constants import MIN_AMOUNT, MIN_COOKING_TIME, MAX_COOKING_TIME
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe,
    Recipe, ShoppingCart, Tag
)
from users.models import Subscription, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.follower.filter(author_id=obj.id).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class CreateIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, value):
        if value < MIN_AMOUNT:
            raise serializers.ValidationError('Укажите количество')
        return value

    class Meta:
        model = IngredientInRecipe
        fields = ['id', 'amount']


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(
        method_name='get_count_recipes'
    )

    class Meta(CustomUserSerializer.Meta):
        model = CustomUser
        fields = CustomUserSerializer.Meta.fields + [
            'recipes',
            'recipes_count'
        ]
        read_only_fields = ['email', 'username', 'first_name', 'last_name']

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = obj.recipes.all()

        if recipes_limit:
            try:
                queryset = queryset[:int(recipes_limit)]
            except ValueError:
                pass

        return RecipeMinifiedSerializer(queryset, many=True).data

    def get_count_recipes(self, obj):
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['user', 'author']

    def validate(self, attrs):
        user = attrs.get('user')
        author = attrs.get('author')

        if user.following.filter(author=author).exists():
            raise serializers.ValidationError(
                detail='Вы уже подписаны',
                code=status.HTTP_400_BAD_REQUEST
            )

        if user == author:
            raise serializers.ValidationError(
                detail='Подписка на самого себя запрещено',
                code=status.HTTP_400_BAD_REQUEST
            )

        return attrs

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='check_is_favorite'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='check_is_in_cart'
    )
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='recipe_ingredient'
    )

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart']

    def check_is_favorite(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.favorites.filter(user=user).exists()
        )

    def check_is_in_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and obj.shopping_carts.filter(user=user).exists()
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'tags', 'ingredients',
                  'text', 'image', 'cooking_time']

    def validate_tags(self, value):
        tags_id_list = set()
        for tag in value:
            if tag.id in tags_id_list:
                raise serializers.ValidationError(
                    'Укажите уникальный тег'
                )
            tags_id_list.add(tag.id)

        if not tags_id_list:
            raise serializers.ValidationError(
                'Укажите хотя бы один тег'
            )

        return value

    def validate_cooking_time(self, value):
        if value and int(value) < MIN_COOKING_TIME:
            raise serializers.ValidationError(
                'Укажите корректное время приготовления'
            )

        if value and int(value) > MAX_COOKING_TIME:
            raise serializers.ValidationError(
                f'Макс. время приготовления {MAX_COOKING_TIME}'
            )

        return value

    def validate_ingredients(self, value):
        ingredients_id_list = set()

        for item in value:
            curr_ingredient = item['id']

            if curr_ingredient.id in ingredients_id_list:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными'
                )

            ingredients_id_list.add(curr_ingredient.id)

        if not ingredients_id_list:
            raise serializers.ValidationError(
                'Укажите хотя бы один ингредиент'
            )

        return value

    @staticmethod
    def create_ingredients(ingredients, recipe):
        ingredients_list = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount']
            )
            for item in ingredients
        ]

        IngredientInRecipe.objects.bulk_create(ingredients_list)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user

        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        recipe.tags.add(*tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        validated_data['author'] = self.context.get('request').user

        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        instance.tags.add(*tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        validators = [
            validators.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в корзину'
            )
        ]

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
