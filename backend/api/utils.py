from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipes
from .serializers import RecipeMinifiedSerializer


def add_del_recipesview(request, model, **kwargs):
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
        serializer = RecipeMinifiedSerializer(
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
        else:
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
