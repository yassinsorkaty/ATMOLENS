from django.test import TestCase
from django.urls import reverse

class WeatherAppTests(TestCase):
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')

    def test_get_cities_view(self):
        response = self.client.get(reverse('get_cities'), {'country': 'US'})
        self.assertEqual(response.status_code, 200)

    def test_get_weather_view(self):
        response = self.client.get(reverse('get_weather'), {'country': 'US', 'city': 'New York'})
        self.assertEqual(response.status_code, 200)