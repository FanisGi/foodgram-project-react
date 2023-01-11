from django_filters import rest_framework as filters
from recipes.models import Recipes, Tags


class RecipesFilter(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        queryset=Tags.objects.all()
    )

    class Meta:
        model = Recipes
        fields = ('tags',)
