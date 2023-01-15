from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import Users

STR_NUMBER = 15


class Tags(models.Model):
    """Модель тегов(Завтрак/Обед/Ужин)."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex='^#[a-fA-F0-9]{6}$',
                message='Введенное занчение не является HEX-кодом цвета.'
            )
        ]
    )
    slug = models.CharField(
        verbose_name='slug',
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex='^[-a-zA-Z0-9_]+$',
                message=(
                    'slug введен неверно. Может состоять из латинских'
                    ' букв, цифр и спецсимвола _'
                )
            )
        ]
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_NUMBER]


class Ingredients(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_NUMBER]


class Recipes(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    author = models.ForeignKey(
        Users,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Список тегов',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингредиенты',
        through='IngredientInRecipe',
        related_name='recipes',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1'),
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='recipe_unique',
            ),
        ]

    def __str__(self):
        return self.name[:STR_NUMBER]


class IngredientInRecipe(models.Model):
    """Модель с дополнением к связке ингредиент - рецепт."""
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='ингредиент',
        related_name='ingredient_inrecipe',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        related_name='ingredientin_recipe',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество ингрединта',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1'),
        ]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class Favorite(models.Model):
    """Модель с избранными рецептами."""
    user = models.ForeignKey(
        Users,
        verbose_name='пользователь',
        related_name='favorite_user',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        related_name='favorite_recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_unique',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Subscriptions(models.Model):
    """Модель с подписками на авторов."""

    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Избранный автор'
        verbose_name_plural = 'Подписки на авторов'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follow_unique',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписался на пользователя {self.author}'


class Shoppingcart(models.Model):
    """Модель списка покупок ингредиентов по рецептам."""
    user = models.ForeignKey(
        Users,
        verbose_name='Пользователь',
        related_name='shoppingcart_user',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='Рецепт',
        related_name='shoppingcart_recipe',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок по рецепту'
        verbose_name_plural = 'Список покупок по рецепту'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_unique',
            ),
        ]

    def __str__(self):
        return f'Список покупок по рецепту {self.recipe}'
