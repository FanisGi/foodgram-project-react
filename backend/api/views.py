from django.db.models import Sum
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Tags, Recipes, Ingredients, Subscriptions, 
    Favorite, Shoppingcart, IngredientInRecipe,
)
from .utils import add_del_recipesview
from .filters import RecipesFilter
from .serializers import (
    TagsSerializer, IngredientsSerializer, CustomUserSerializer, RecipesSerializer,
    SubscriptionsSerializer, RecipeMinifiedSerializer, RecipesAddSerializer,
)

User = get_user_model()


class CustomUsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    # permission_classes=(IsAuthenticated,)

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

    @action(detail=False)
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

        return add_del_recipesview(
            request, Favorite, RecipeMinifiedSerializer, **kwargs
        )

    @action(
        detail=False,
        methods=['GET'],
    )
    def download_shopping_cart(self, request):
        """Скачать файл со списком покупок. Формат TXT."""

        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__shoppingcart_recipe__user = request.user,
        ).order_by('ingredient__name').values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        shopping_list = f'Список покупок {request.user}:\n'
        for iter, (name, unit, amount) in enumerate(shopping_cart, start=1):
            shopping_list += f'\n {iter}. {name} ({unit}) - {amount}'

        filename = 'data.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def shopping_cart(self, request, **kwargs):
        """Добавить или удалить рецепт из списка покупок."""

        return add_del_recipesview(
            request, Shoppingcart, RecipeMinifiedSerializer, **kwargs
        )
