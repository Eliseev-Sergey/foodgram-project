from django.core.validators import (
    MaxValueValidator, MinValueValidator, RegexValidator
)
from django.db import models

from users.models import CustomUser
from recipes.constants import (
    COLOR_FIELD_LEN,
    FIELD_DEFAULT_LEN,
    HEX_COLOR_REGEX,
    MIN_AMOUNT,
    MIN_COOKING_TIME,
    MAX_AMOUNT,
    MAX_COOKING_TIME,
    UNIT_LEN
)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=FIELD_DEFAULT_LEN
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=UNIT_LEN
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='ingredients_unique'
        )]

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название', unique=True, max_length=FIELD_DEFAULT_LEN
    )
    color = models.CharField(
        verbose_name='Цветовой код',
        unique=True,
        max_length=COLOR_FIELD_LEN,
        validators=[RegexValidator(
            regex=HEX_COLOR_REGEX,
            message='Неверный формат'
        )],
        help_text='Например, #49B64E'
    )
    slug = models.SlugField(
        verbose_name='SLUG', unique=True, max_length=FIELD_DEFAULT_LEN
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название', max_length=FIELD_DEFAULT_LEN, unique=True
    )
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        verbose_name='Картинка', upload_to='recipes/images/'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientInRecipe', verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Мин. время приготовления {MIN_COOKING_TIME}'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Макс. время приготовления {MAX_COOKING_TIME}'
            ),
        ]
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Рецепты'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=f'Мин. кол-во ингредиентов {MIN_AMOUNT}'),
            MaxValueValidator(
                MAX_AMOUNT,
                message=f'Макс. кол-во ингредиентов {MAX_AMOUNT}'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='ingredientinrecipes_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorites_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - добавлено в избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_carts_unique'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name} - добавлено в список покупок'
