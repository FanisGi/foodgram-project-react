from django.shortcuts import get_object_or_404
from recipes.models import (IngredientInRecipe, Ingredients, Recipes,
                            Subscriptions)
from rest_framework import status
from rest_framework.response import Response


def add_del_recipesview(request, model, recipeminifiedserializer, **kwargs):
    """
    Утилита для view функции recipes. Применяется для:
    Добавить или удалить рецепт в избранных у пользователя.
    Добавить или удалить рецепт из списка покупок.
    """
    recipe_id = kwargs['pk']
    user = request.user
    recipe_obj = get_object_or_404(Recipes, pk=recipe_id)
    data = {
        "id": recipe_id,
        "name": recipe_obj.name,
        "image": recipe_obj.image,
        "cooking_time": recipe_obj.cooking_time,
    }

    if request.method == 'POST':
        serializer = recipeminifiedserializer(
            instance=data,
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            model.objects.create(
                user=user, recipe_id=recipe_id
            )
            return Response(
                serializer.data, status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method == 'DELETE':
        get_object_or_404(
            model,
            user=user,
            recipe_id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


def boolean_serializers_item(self, model, obj):

    """
    Утилита для получения булевой переменной в сериализаторах:

    1. CustomUserSerializer - get_is_subscribed:
    Подписан ли текущий пользователь на запрашимаего пользователя.

    2. RecipesSerializer - get_is_favorited:
    Показывает, находится ли рецепт в списке избранных.

    3. RecipesSerializer - get_is_shopping_cart:
    Показывает, находится ли рецепт в списке покупок.
    """
    user = self.context.get('request').user

    if user.is_anonymous:
        return False

    if model == Subscriptions:
        if model.objects.filter(
            author_id=obj.id,
            user=user
        ).exists():
            return True
        return False

    if model.objects.filter(
        recipe_id=obj.id,
        user=user
    ).exists():
        return True
    return False


def create_update_recipes(validated_data, author=None, instance=None):
    """Утилита для RecipesSerializer для методов create, update."""
    tags = validated_data.pop('tags')
    ingredients = validated_data.pop('ingredientin_recipe')

    if instance is None:
        recipe = Recipes.objects.create(author=author, **validated_data)
    else:
        recipe = instance

    recipe.tags.set(tags)

    IngredientInRecipe.objects.bulk_create([
        IngredientInRecipe(
            recipe=recipe,
            amount=ingredient.get('amount'),
            ingredient=Ingredients.objects.get(
                id=ingredient.get('id')
            ),
        ) for ingredient in ingredients
    ])

    return recipe
