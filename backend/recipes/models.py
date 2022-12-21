from django.db import models
from django.core.validators import MinValueValidator

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
    )
    slug = models.SlugField(
        verbose_name='slug',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'
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
    tags = models.ForeignKey(
        Tags,
        verbose_name='Список id тегов',
        on_delete=models.CASCADE,
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
        verbose_name = 'Ресепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:STR_NUMBER]


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        verbose_name='ингредиент',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipes,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество ингрединта',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1'),
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'
