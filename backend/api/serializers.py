import base64

from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
# from django.shortcuts import get_object_or_404
# from django.forms import ValidationError
from rest_framework import serializers

from recipes.models import (
    Tags, Recipes, IngredientInRecipe, Ingredients, Subscriptions
)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    username = serializers.CharField(required=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, request):
        """Подписан ли текущий пользователь на запрашимаего пользователя."""

        if Subscriptions.objects.filter(
            author_id=request.id,
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


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    tags = TagsSerializer()
    # ingredients = serializers.SlugRelatedField(
    #     slug_field='recipe_id', queryset=IngredientInRecipe.objects.all()
    # )

    class Meta:
        model = Recipes
        fields = '__all__'


class RecipeMinifiedSeriakizer(serializers.ModelSerializer):
    """
    Краткий вариант сериализатора c рецептами. 
    Состоит из id, name, image, cooking_time.
    """

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',) 


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, request):
        """
        Функция выдаёт список рецептов автора, 
        на которого подписан пользователь. 
        В каждом списке хранится id, name, image, cooking_time.
        """

        recipes_data = Recipes.objects.filter(
            author=request.id
        )
        serializer = RecipeMinifiedSeriakizer(
            data=recipes_data, 
            many=True
        )
        serializer.is_valid()
        return serializer.data
    
    def get_recipes_count(self, request):
        """Количество рецептов у избранного автора."""

        return request.recipes.count()
    
    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        )
