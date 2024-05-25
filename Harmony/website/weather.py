from flask import Flask, Blueprint, render_template, redirect, request, jsonify, session
import requests
from dotenv import load_dotenv
import os
from dataclasses import dataclass

load_dotenv() # loads environment files
weather_api_key = os.getenv('WEATHER_API_KEY')

weather = Blueprint('weather', __name__)

@dataclass
class WeatherData: 
    main: str
    description: str
    icon: str
    temp: float

def get_lat_lon(city_name, state_code, country_code, API_key): 
    response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&appid={API_key}').json()
    data = response[0] #returns a dict
    lat = data.get('lat')
    lon = data.get('lon')
    return lat, lon

def get_weather(lat, lon, API_key):
    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}&units=metric').json()
    data = WeatherData(
        main=response.get('weather')[0].get('main'),
        description=response.get('weather')[0].get('description'),
        icon=response.get('weather')[0].get('icon'),
        temp=response.get('main').get('temp')
    )
    return data

@weather.route('/todays_playlist', methods=['GET', 'POST'])
def today():
    if request.method == 'POST':
        city = request.form.get("CityName")
        state = request.form.get("StateName")
        country = request.form.get("CountryName")
        lat, lon = get_lat_lon(city, state, country, weather_api_key)
        weather_data = get_weather(lat, lon, weather_api_key)
        print(weather_data)
    return render_template('playlist_of_the_day.html')

if __name__ == '__main__':
    lat, lon = get_lat_lon('Toronto', 'ON', 'CA', weather_api_key)
    print(get_weather(lat, lon, weather_api_key))

print(get_lat_lon('Toronto', 'ON','CA', weather_api_key))
