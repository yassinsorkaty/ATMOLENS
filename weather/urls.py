# weather/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),           # main page
    path('get_cities/', views.get_cities, name='get_cities'),
    path('get_weather/', views.get_weather, name='get_weather'),
    path('weather_map/', views.weather_map, name='weather_map'),
    path('get_map_weather/', views.get_map_weather, name='get_map_weather'),
    path('get_location_details/', views.get_location_details, name='get_location_details'),
]
