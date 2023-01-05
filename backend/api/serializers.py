from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserSerializer
# from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators
from rest_framework.response import Response

from recipes.models import (
    Tags, Recipes, IngredientInRecipe, Ingredients, Subscriptions,
    Favorite, Shoppingcart
)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """
        Подписан ли текущий пользователь на запрашимаего пользователя.
        """

        if Subscriptions.objects.filter(
            author_id=obj.id,
            user=self.context.get('request').user
        ).exists():
            return True

        return False


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор Tags."""

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов."""

    class Meta:
        model = Ingredients
        fields = '__all__'


class IngredientsInRecipesSerializers(serializers.ModelSerializer):
    """Сериализатор для связки рецепт-игредиент-количество."""
    
    id = serializers.IntegerField(
        # source='ingredient_id'
        )
    # amount = serializers.IntegerField()
    # # ingredient = serializers.IntegerField(source='id')
    
    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Краткий вариант сериализатора c рецептами. 
    Состоит из id, name, image, cooking_time.
    """
    image = Base64ImageField(
        # Для тестов, удалить перед слиянием
        required=False, allow_null=True
    )

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',)
        # read_only_fields = ('name', 'image', 'cooking_time',)


class RecipesSerializer(RecipeMinifiedSerializer):
    """Сериализатор рецептов для чтения данных."""

    author = CustomUserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        """Игредиенты рецепта с требуемым количеством."""

        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_inrecipe__amount')
        )

    def get_is_favorited(self, obj):
        """
        Показывает, находится ли рецепт в списке избранных.
        """

        if Favorite.objects.filter(
            recipe_id=obj.id,
            user=self.context.get('request').user
        ).exists():
            return True

        return False
    
    def get_is_in_shopping_cart(self, obj):
        """
        Показывает, находится ли рецепт в списке покупок.
        """

        if Shoppingcart.objects.filter(
            recipe_id=obj.id,
            user=self.context.get('request').user
        ).exists():
            return True

        return False

    class Meta(RecipeMinifiedSerializer.Meta):
        model = Recipes
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart'
        ) + RecipeMinifiedSerializer.Meta.fields


class RecipesAddSerializer(RecipeMinifiedSerializer):
    """Сериализатор рецептов для создания и редактирования данных."""

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tags.objects.all())
    ingredients = IngredientsInRecipesSerializers(source='ingredientin_recipe', many=True)

    class Meta(RecipeMinifiedSerializer.Meta):
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'text',
        ) + RecipeMinifiedSerializer.Meta.fields
        # validators = validators.UniqueTogetherValidator(
        #     queryset=Recipes.objects.all(),
        #     fields=['name', 'author']
        # )

    def create(self, validated_data):
        """Создание нового рецепта."""

        ingredients = validated_data.pop('ingredientin_recipe')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipes.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient.get('amount')
            current_ingredient = Ingredients.objects.get(
                id = ingredient.get('id')
            )
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        
        return recipe
    
    def to_representation(self, instance):
        """Переопределение Response-ответа."""
        
        context = {'request': self.context.get('request')}
        serializer = RecipesSerializer(
            instance=instance,
            context=context
        )
        return serializer.data


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        """
        Функция выдаёт список рецептов автора, 
        на которого подписан пользователь. 
        В каждом списке хранится id, name, image, cooking_time.
        """

        recipes_data = Recipes.objects.filter(
            author=obj.id
        )
        serializer = RecipeMinifiedSerializer(
            data=recipes_data, 
            many=True
        )
        serializer.is_valid()
        return serializer.data
    
    def get_recipes_count(self, obj):
        """Количество рецептов у избранного автора."""

        return obj.recipes.count()
    
    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        )
        read_only_fields = ('email', 'username',)
