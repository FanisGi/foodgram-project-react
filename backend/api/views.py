from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework import status, viewsets
# from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Tags, Recipes, Ingredients, Subscriptions, Favorite, Shoppingcart,
    IngredientInRecipe,
)
from .filters import RecipesFilter
from .serializers import (
    TagsSerializer, RecipesSerializer, IngredientsSerializer, CustomUserSerializer,
    SubscriptionsSerializer, RecipeMinifiedSerializer, RecipesAddSerializer,
)

User = get_user_model()


class CustomUsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes=(IsAuthenticated,)

    @action(
        detail=True,
        methods=['POST', 'DELETE']
    )
    def subscribe(self, request, **kwargs):
        """Подписаться или отписать на пользователя."""

        user = request.user
        author_id = kwargs['id']
        author_obj = get_object_or_404(User, id=author_id)

        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                instance=author_obj,
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                Subscriptions.objects.create(
                    user=user, author_id=author_id
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
                Subscriptions,
                user=user,
                author_id=author_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
    )
    def subscriptions(self, request):
        """
        Возвращает пользователей, 
        на которых подписан текущий пользователь. 
        В выдачу добавляются рецепты.
        """

        subscriptions_data = User.objects.filter(
            following__user=request.user
        )
        page = self.paginate_queryset(subscriptions_data)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


class ingredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter    

    def get_serializer_class(self):
        """
        Возвращает нужный сериализатор при разных операциях: 
        GET, DELETE - RecipesSerializer; 
        POST, UPDATE - RecipesAddSerializer.
        """

        if self.action in ('create', 'partial_update'):
            return RecipesAddSerializer 
        return RecipesSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class = RecipeMinifiedSerializer
    )
    def favorite(self, request, **kwargs):
        """Добавить или удалить рецепт в избранных у пользователя."""

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
                Favorite.objects.create(
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
                Favorite,
                user=user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
    )
    def download_shopping_cart(self, request, **kwargs):
        """Скачать файл со списком покупок. Формат TXT."""

        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__shoppingcart_recipe__user = request.user,
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount',
        )

        shopping_list = {}
        for name, unit, amount in shopping_cart:
            if name in shopping_list:
                shopping_list[name]['amount'] += amount
            else:
                shopping_list[name] = {'unit': unit, 'amount': amount}
        
        content = f'Список покупок {request.user}'
        for name, unit, amount in shopping_cart:
            content += (
                f'\n'
                f'{name} - {shopping_list[amount]} - {shopping_list[unit]}'
            )
        file = 'data.txt'
        # Протестировать с 'application/pdf' после слияния
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={0}'.format(file)
        return response

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def shopping_cart(self, request, **kwargs):
        """Добавить или удалить рецепт из списка покупок."""
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
                Shoppingcart.objects.create(
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
                Shoppingcart,
                user=user,
                recipe_id=recipe_id
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)