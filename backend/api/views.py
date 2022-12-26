from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
# from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
# from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Tags, Recipes, Ingredients, Subscriptions
)
from .filters import RecipesFilter
# # from .permissions import (IsAdminOnly, IsAdminOrReadOnly,
#                           ModeratorOwnerOrReadOnly)
from .serializers import (
    TagsSerializer, RecipesSerializer, IngredientsSerializer, CustomUserSerializer,
    SubscriptionsSerializer, 
)
# from .utils import send_code

User = get_user_model()


class CustomUsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes=(IsAuthenticated,)

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

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def subscribe(self, request):
        """
        Подписаться или отписать на пользователя.
        """
        print('sadasdasdsadasdsadasd sad sa d')
        user = request.user
        author = request.id

        if request.method == 'POST':
            serializer = SubscriptionsSerializer(
                data = request.data,
                context={"request": request}
            )
            if serializer.is_valid():
                user = request.user
                author_id = request.id
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
            subscription = get_object_or_404(
                Subscriptions,
                user=user,
                author_id=author_id
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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
