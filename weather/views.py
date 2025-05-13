from django.conf import settings

api_key = settings.OPENWEATHER_API_KEY
from django.shortcuts import render
import requests
from django.http import HttpResponse, JsonResponse
from django_countries import countries
from cities_light.models import City
import datetime

def index(request):
    country_list = list(countries)
    return render(request, 'weather/index.html', {
        'countries': country_list,
        'api_key': settings.OPENWEATHER_API_KEY,
        'active_page': 'atmo_check'
    })

def get_cities(request):
    country_code = request.GET.get('country')
    if not country_code:
        return HttpResponse("No country code provided", status=400)
    
    # Get cities for the selected country
    cities = City.objects.filter(
        country__code2=country_code
    ).values_list('name', flat=True).order_by('name')
    
    if not cities:
        return HttpResponse("No cities found for the selected country.", status=404)
    
    return render(request, 'weather/cities_dropdown_list_options.html', {'cities': cities})

def get_weather_recommendations(temp, description, humidity, wind_speed):
    recommendations = []
    
    # Temperature-based recommendations
    if temp <= 0:
        recommendations.append({
            'type': 'danger',
            'icon': 'bi-thermometer-snow',
            'title': 'Extreme Cold',
            'text': 'Wear multiple layers, gloves, and a warm hat. Limit outdoor exposure.'
        })
    elif temp < 10:
        recommendations.append({
            'type': 'warning',
            'icon': 'bi-thermometer-low',
            'title': 'Cold Weather',
            'text': 'Wear a warm jacket, scarf, and appropriate winter clothing.'
        })
    elif temp > 30:
        recommendations.append({
            'type': 'danger',
            'icon': 'bi-thermometer-high',
            'title': 'High Temperature',
            'text': 'Stay hydrated, wear light clothing, and avoid prolonged sun exposure.'
        })
    elif temp > 25:
        recommendations.append({
            'type': 'warning',
            'icon': 'bi-sun',
            'title': 'Warm Weather',
            'text': 'Stay hydrated and wear light, breathable clothing.'
        })

    # Weather condition-based recommendations
    if 'rain' in description:
        recommendations.append({
            'type': 'info',
            'icon': 'bi-umbrella',
            'title': 'Rainy Conditions',
            'text': 'Carry an umbrella and wear waterproof shoes.'
        })
    elif 'snow' in description:
        recommendations.append({
            'type': 'info',
            'icon': 'bi-snow',
            'title': 'Snowy Conditions',
            'text': 'Wear boots with good traction and warm, waterproof clothing.'
        })
    elif 'clear' in description:
        if temp > 20:
            recommendations.append({
                'type': 'success',
                'icon': 'bi-sun',
                'title': 'Perfect Weather',
                'text': 'Great conditions for outdoor activities!'
            })
    elif 'storm' in description:
        recommendations.append({
            'type': 'danger',
            'icon': 'bi-cloud-lightning',
            'title': 'Stormy Weather',
            'text': 'Stay indoors and avoid open areas.'
        })

    # Humidity-based recommendations
    if humidity > 80:
        recommendations.append({
            'type': 'info',
            'icon': 'bi-moisture',
            'title': 'High Humidity',
            'text': 'High moisture levels. Stay hydrated and wear breathable clothing.'
        })
    elif humidity < 30:
        recommendations.append({
            'type': 'info',
            'icon': 'bi-droplet',
            'title': 'Low Humidity',
            'text': 'Dry conditions. Keep moisturized and stay hydrated.'
        })

    # Wind-based recommendations
    if wind_speed > 15:
        recommendations.append({
            'type': 'warning',
            'icon': 'bi-wind',
            'title': 'Strong Winds',
            'text': 'Be careful with loose objects and consider indoor activities.'
        })

    return recommendations

def get_weather(request):
    country = request.GET.get('country')
    city = request.GET.get('city')
    
    if not country or not city:
        return HttpResponse("City and country are required", status=400)
        
    API_KEY = settings.OPENWEATHER_API_KEY
    
    # Current weather request
    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&units=metric&appid={API_KEY}"
    
    # Forecast request
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},{country}&units=metric&appid={API_KEY}"
    
    try:
        # Get current weather
        current_res = requests.get(current_url, timeout=5)
        current_data = current_res.json()
        
        # Get forecast
        forecast_res = requests.get(forecast_url, timeout=5)
        forecast_data = forecast_res.json()
        
        if current_res.status_code != 200 or forecast_res.status_code != 200:
            raise ValueError(current_data.get("message", "Weather data not found"))
            
        # Process current weather
        weather = current_data['weather'][0]
        main = current_data['main']
        
        # Get recommendations
        recommendations = get_weather_recommendations(
            temp=main['temp'],
            description=weather['description'].lower(),
            humidity=main['humidity'],
            wind_speed=current_data['wind']['speed']
        )

        city_timezone_offset = forecast_data['city']['timezone']  # in seconds

        forecast_list = []
        for item in forecast_data['list'][:8]:  # Next 24 hours (8 * 3 hours)
            # Parse UTC datetime
            dt_utc = datetime.datetime.strptime(item['dt_txt'], "%Y-%m-%d %H:%M:%S")
            # Add timezone offset
            dt_local = dt_utc + datetime.timedelta(seconds=city_timezone_offset)
            forecast_list.append({
                'datetime': dt_local,
                'temp': item['main']['temp'],
                'description': item['weather'][0]['description'].title(),
                'icon': item['weather'][0]['icon'],
                'humidity': item['main']['humidity']
            })
        
        context = {
            'city': city,
            'country': country,
            'description': weather['description'].title(),
            'icon': weather['icon'],
            'temperature': main['temp'],
            'humidity': main['humidity'],
            'forecast': forecast_list,
            'recommendations': recommendations
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        context = {'error': str(e)}

    return render(request, 'weather/weather_display.html', context)

def weather_map(request):
    """View for displaying the interactive weather map"""
    return render(request, 'weather/weather_map.html', {
        'api_key': settings.OPENWEATHER_API_KEY,
        'active_page': 'atmo_map'
    })

def get_map_weather(request):
    if request.method == 'GET':
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        api_key = settings.OPENWEATHER_API_KEY
        
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric'
        
        try:
            response = requests.get(url)
            data = response.json()
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
