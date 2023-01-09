from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Tags, Recipes, IngredientInRecipe, Ingredients, Subscriptions,
    Favorite, Shoppingcart
)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """
        Подписан ли текущий пользователь на запрашимаего пользователя.
        """

        if Subscriptions.objects.filter(
            author_id=obj.id,
            user=self.context.get('request').user
        ).exists():
            return True

        return False


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


class IngredientsInRecipesSerializers(serializers.ModelSerializer):
    """Сериализатор для связки рецепт-игредиент-количество."""
    
    id = serializers.IntegerField(
        # source='ingredient_id'
        )
    # amount = serializers.IntegerField()
    # # ingredient = serializers.IntegerField(source='id')
    
    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Краткий вариант сериализатора c рецептами. 
    Состоит из id, name, image, cooking_time.
    """
    image = Base64ImageField(
        required=False, allow_null=True
    )

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('name', 'image', 'cooking_time',)


class RecipesSerializer(RecipeMinifiedSerializer):
    """Сериализатор рецептов для чтения данных."""

    author = CustomUserSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeMinifiedSerializer.Meta):
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 
            'is_favorited', 'is_in_shopping_cart', 'text',
        ) + RecipeMinifiedSerializer.Meta.fields
    
    def get_ingredients(self, obj):
        """Игредиенты рецепта с требуемым количеством."""

        return obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_inrecipe__amount')
        )

    def get_is_favorited(self, obj):
        """
        Показывает, находится ли рецепт в списке избранных.
        """

        if Favorite.objects.filter(
            recipe_id=obj.id,
            user=self.context.get('request').user
        ).exists():
            return True

        return False
    
    def get_is_in_shopping_cart(self, obj):
        """
        Показывает, находится ли рецепт в списке покупок.
        """

        if Shoppingcart.objects.filter(
            recipe_id=obj.id,
            user=self.context.get('request').user
        ).exists():
            return True

        return False
        

class RecipesAddSerializer(RecipeMinifiedSerializer):
    """Сериализатор для создания и редактирования рецептов."""

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tags.objects.all())
    ingredients = IngredientsInRecipesSerializers(source='ingredientin_recipe', many=True)

    class Meta(RecipeMinifiedSerializer.Meta):
        model = Recipes
        fields = (
            'id', 'tags', 'author', 'ingredients', 'text',
        ) + RecipeMinifiedSerializer.Meta.fields

    def validate_name(self, data):
        """Проверка на повторение рецептов одним автором."""

        author = self.context.get('request').user
        name_recipe = self.initial_data.get('name')
        if Recipes.objects.filter(
            author=author,
            name=name_recipe
        ).exists():
            raise serializers.ValidationError(
                f'У Вас уже есть рецепт с именем {name_recipe}. '
                'Проверьте свой рецепт.'
            )
        return data
    
    def validate_tags(self, data):
        """Проверка на выбор Tags. Min_value = 1."""

        tags = self.initial_data.get('tags')
        if len(tags) == 0:
            raise serializers.ValidationError(
                'Выберите хотя бы 1 Tags.'
            )
        return data

    def validate_ingredients(self, data):
        """Проверка на ингредиентов."""

        ingredients = self.initial_data.get('ingredients')
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Выберите хотя бы 1 ингредиент из списка.'
            )
        ingredients_id = []
        for ingredient in ingredients:
            print(ingredient.get('id'))
            if ingredient.get('id') in ingredients_id:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторятся. '
                    'Проверьте свой рецепт.'
                )
            if ingredient.get('amount') in (None, 0):
                raise serializers.ValidationError(
                    'Количество ингредиента обязательно для заполнения. '
                    'Минимальное значение 1.'
                )
            ingredients_id.append(ingredient.get('id'))
        return data

    def create(self, validated_data):
        """Создание нового рецепта."""

        ingredients = validated_data.pop('ingredientin_recipe')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipes.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient.get('amount')
            current_ingredient = Ingredients.objects.get(
                id = ingredient.get('id')
            )
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        
        return recipe
    
    def update(self, instance, validated_data):
        """Обновление рецепта."""

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)

        old_ingredients = IngredientInRecipe.objects.filter(recipe_id=instance.id)
        old_ingredients.delete()
        new_ingredients = validated_data.pop('ingredientin_recipe')

        for ingredient in new_ingredients:
            current_ingredient = Ingredients.objects.get(
                id = ingredient.get('id')
            )
            amount = ingredient.get('amount')
            IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient=current_ingredient,
                    amount=amount
                )

        instance.save()
        return instance

    def to_representation(self, instance):
        """Переопределение Response-ответа."""
        
        context = {'request': self.context.get('request')}
        serializer = RecipesSerializer(
            instance=instance,
            context=context
        )
        return serializer.data


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count',)
        )
        read_only_fields = ('email', 'username',)

    def validate(self, data):
        """Проверка подписок пользователя."""

        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Subscriptions.objects.filter(
            user=user, author=author
        ).exists():
            raise serializers.ValidationError(
                f'Вы уже подписаны на {author}.'
            )
        return data

    def get_recipes(self, obj):
        """
        Функция выдаёт список рецептов автора, 
        на которого подписан пользователь. 
        В каждом списке хранится id, name, image, cooking_time.
        """

        recipes_data = Recipes.objects.filter(
            author=obj.id
        )
        serializer = RecipeMinifiedSerializer(
            data=recipes_data, 
            many=True
        )
        serializer.is_valid()
        return serializer.data
    
    def get_recipes_count(self, obj):
        """Количество рецептов у избранного автора."""

        return obj.recipes.count()
