import base64

from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
# from django.shortcuts import get_object_or_404
# from django.forms import ValidationError
from rest_framework import serializers

from recipes.models import (
    Tags, Recipes, IngredientInRecipe, Ingredients, Subscriptions
)
# from .validators import is_correct_email, is_correct_username

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    username = serializers.CharField(required=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Подписан ли текущий пользователь на запрашимаего пользователя."""
        if Subscriptions.objects.filter(user=self.username):
            return 'true'

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )

        user.save()

        return user

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
        slug_field='username', read_only=True, default=serializers.CurrentUserDefault()
    )
    tags = TagsSerializer()
    # ingredients = serializers.SlugRelatedField(
    #     slug_field='recipe_id', queryset=IngredientInRecipe.objects.all()
    # )

    class Meta:
        model = Recipes
        fields = '__all__'
