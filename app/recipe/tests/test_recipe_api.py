from rest_framework import status
from rest_framework.test import APIClient  # to make request
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')  # app/identifier


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
