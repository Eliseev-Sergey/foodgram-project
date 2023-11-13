from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag
)
from recipes.validators import IngredientRecipeValidator


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientInRecipeAdmin(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 0
    validate_min = True
    formset = IngredientRecipeValidator


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (IngredientInRecipeAdmin,)
    readonly_fields = ('favorites_count',)

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = 'Добавлено в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name', 'user__username')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('recipe__tags',)
    search_fields = ('recipe__name', 'user__username')
