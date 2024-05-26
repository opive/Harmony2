import requests
from flask import Flask, Blueprint, render_template, request
from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv()  # Load environment variables
weather_api_key = os.getenv('WEATHER_API_KEY')

weather = Blueprint('weather', __name__)

@dataclass
class WeatherData:
    main: str
    description: str
    icon: str
    temp: float

def get_lat_lon(city_name, state_code, country_code, API_key):
    response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}')
    data = response.json()
    if data:
        lat = data[0].get('lat')
        lon = data[0].get('lon')
        return lat, lon
    return None, None

def get_weather(lat, lon, API_key):
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units=metric')
    data = response.json()
    if 'weather' in data and 'main' in data:
        weather_data = WeatherData(
            main=data['weather'][0].get('main'),
            description=data['weather'][0].get('description'),
            icon=data['weather'][0].get('icon'),
            temp=data['main'].get('temp')
        )
        return weather_data
    return None

@weather.route('/todays_playlist', methods=['GET', 'POST'])
def today():
    weather_data = None
    if request.method == 'POST':
        city = request.form.get("CityName")
        state = request.form.get("StateName")
        country = request.form.get("CountryName")
        lat, lon = get_lat_lon(city, state, country, weather_api_key)
        if lat and lon:
            weather_data = get_weather(lat, lon, weather_api_key)
    return render_template('playlist_of_the_day.html', data=weather_data)

if __name__ == '__main__':
    lat, lon = get_lat_lon('Toronto', 'ON', 'CA', weather_api_key)
    print(get_weather(lat, lon, weather_api_key))

print(get_lat_lon('Toronto', 'ON', 'CA', weather_api_key))
