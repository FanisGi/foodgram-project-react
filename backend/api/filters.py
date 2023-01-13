from django_filters import rest_framework as filters
from recipes.models import Recipes, Tags, Favorite, Shoppingcart, Ingredients


class IngredientsFilter(filters.FilterSet):

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipesFilter(filters.FilterSet):
    """
    Фильтрация рецептов по нескольким тегам в комбинации «или».
    Метод filter_is_favorited - фильтрует queryset по избранных рецептам. 
    Метод filter_is_in_shopping_cart - фильтрует queryset по авторам, 
    на которых подписан пользователь.
    """
    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='slug',
        queryset=Tags.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipes
        fields = ('tags',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if Favorite.objects.filter(user=user).exists():
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if Shoppingcart.objects.filter(user=user).exists():
            return queryset.filter(shoppingcart_recipe__user=user)
        return queryset
