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
    Tags, Recipes, Ingredients,
)
from .filters import RecipesFilter
# # from .permissions import (IsAdminOnly, IsAdminOrReadOnly,
#                           ModeratorOwnerOrReadOnly)
from .serializers import (
    TagsSerializer, RecipesSerializer, IngredientsSerializer, CustomUserSerializer,

)
# from .utils import send_code

User = get_user_model()


class CustomUsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes=(IsAuthenticated,)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes=(AllowAny,)


class ingredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes=(AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
