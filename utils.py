from dotenv import load_dotenv
import requests
import os

load_dotenv()

def get_weather(location):
    """
    Fetches current weather information for a given location using the OpenWeatherMap API.

    Args:
        location (str): The name of the city or location to retrieve weather data for.

    Returns:
        dict or None: A dictionary containing weather details such as location, country, temperature, feels_like, humidity, description, and wind_speed if successful; otherwise, None if an error occurs.
    """
    
    
    BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'
    
    params = {
        'q': location,
        'appid': os.environ.get("WEATHER_API_KEY"),
        'units': 'metric' 
    }
    
    try:
        response = requests.get(BASE_URL, params=params)

        response.raise_for_status()

        weather_data = response.json()
        weather_info = {
            'location': weather_data['name'],
            'country': weather_data['sys']['country'],
            'temperature': weather_data['main']['temp'],
            'feels_like': weather_data['main']['feels_like'],
            'humidity': weather_data['main']['humidity'],
            'description': weather_data['weather'][0]['description'],
            'wind_speed': weather_data['wind']['speed']
        }

        print(f"###GET WEATHER:\n{weather_info}")

        return weather_info
    
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None