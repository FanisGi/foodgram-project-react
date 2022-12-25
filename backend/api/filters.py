from django_filters import rest_framework as filters

from recipes.models import Recipes


class RecipesFilter(filters.FilterSet):
    author = filters.CharFilter(
        field_name='author',
        lookup_expr='icontains'
    )
    tags = filters.CharFilter(
        field_name='tags',
        lookup_expr='icontains'
    )
    # genre = filters.CharFilter(
    #     field_name='genre__slug',
    #     lookup_expr='icontains'
    # )

    class Meta:
        model = Recipes
        fields = ('author', 'tags',)
