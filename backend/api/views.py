from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import CustomIngredientFilter, CustomRecipeFilter
from api.mixins import ListRetrieveMixin
from api.pagination import CustomPagination
from api.serializers import (
    CreateRecipeSerializer, CustomUserSerializer,
    FavoriteSerializer, IngredientSerializer,
    ShoppingCartSerializer, SubscriptionCreateSerializer,
    SubscriptionSerializer, RecipeListSerializer, TagSerializer
)
from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, Recipe, ShoppingCart, Tag
)
from users.models import Subscription, CustomUser


class IngredientViewSet(ListRetrieveMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = CustomIngredientFilter


class TagViewSet(ListRetrieveMixin):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination
    lookup_field = 'id'

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(CustomUser, id=id)

        if request.method == 'POST':
            serializer = SubscriptionCreateSerializer(
                data={'user': user.id, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Subscription,
            user=request.user,
            author=get_object_or_404(CustomUser, id=id)
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        queryset = CustomUser.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)

        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.validated_data['author'] = self.request.user
        serializer.save()
        serializer = CreateRecipeSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data)
        )

    def perform_update(self, serializer):
        return serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return CreateRecipeSerializer

    @action(detail=True, methods=['POST'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'recipe': recipe.id, 'user': request.user.id}

        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            recipe__id=pk,
            user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'recipe': recipe.id, 'user': request.user.id}

        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            recipe__id=pk,
            user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        filename = 'shop_carts.txt'

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount')).order_by('ingredient__name')

        shop_carts = ''
        current_ingr = None
        total_amount = 0

        for ingredient in ingredients:
            name = ingredient.get('ingredient__name')
            measurement_unit = ingredient.get('ingredient__measurement_unit')
            ingredient_amount = ingredient.get('total_amount')

            if current_ingr and current_ingr != name:
                shop_carts += (
                    f'{current_ingr} {measurement_unit} - {total_amount}\n'
                )
                total_amount = 0

            current_ingr = name
            total_amount += ingredient_amount

        if current_ingr:
            shop_carts += (
                f'{current_ingr} {measurement_unit} - '
                f'{total_amount}\n'
            )

        headers = {
            'Content-Disposition': f'attachment; filename={filename}'
        }

        with open(filename, 'w', encoding='UTF-8') as file:
            file.write(shop_carts)

        return FileResponse(open(filename, 'rb'), headers=headers)
