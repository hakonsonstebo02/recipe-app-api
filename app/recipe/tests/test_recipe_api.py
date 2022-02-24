from rest_framework import status
from rest_framework.test import APIClient  # to make request
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')  # app/identifier


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])  # api/recipe/id


def sample_tag(user, name='Main course'):
    """Create and return a simple tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """create and return a sample recipe"""
    default = {
        'title': 'sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    default.update(params)
    return Recipe.objects.create(user=user, **default)


class PublicRecipeTest(TestCase):
    """Test unauthicated recipe access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@dev.com', 'testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrive a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_limited_to_user(self):
        user2 = get_user_model().objects.create_user('other@dev.com', 'test123')
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_view_recipe_detail(self):
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.data, serializer.data)
