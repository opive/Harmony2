import requests
from flask import Flask, Blueprint, render_template, request, redirect, session
from dotenv import load_dotenv
import os
from dataclasses import dataclass
from datetime import datetime


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
            if weather_data: 
                playlist = get_todays_playlist(weather_data.description)
    return render_template('playlist_of_the_day.html', data=weather_data, playlist = playlist)

def get_track_ids(description):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = { #headers include the access token for spotify to identify
        'Authorization' : f"Bearer {session['access_token']}"

    }

    limit = 22
    response = requests.get(os.getenv("API_BASE_URL") + f'/me/playlists', headers=headers)
    if response.status_code == 200:
        playlists = response.json().get('items', []) #json response returns a dictionary. If the key 'items' is not in the dictionary, 
        # it returns an empty list ([].
        track_ids = []
        for playlist in playlists:
            playlist_id = playlist['id']
            response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
            if response.status_code == 200:
                tracks = response.json().get('items', [])
                for track in tracks:
                    track_ids.append(track['track']['id'])
    
    return track_ids

mood_characteristics = { #uses Spotify's parameters for songs to further narrow down a song to a mood
    'happy': {
        'min_energy': 0.7,
        'target_danceability': 0.8,
        'min_tempo': 100
    },
    'relax': {
        'min_energy': 0.4,
        'target_danceability': 0.5,
        'min_tempo': 70
    },
    'chill': {
        'min_energy': 0.3,
        'target_danceability': 0.6,
        'min_tempo': 70
    },
    'melancholy': {
        'min_energy': 0.3,
        'target_danceability': 0.4,
        'max_tempo': 80
    },
    'deep': {
        'min_energy': 0.6,
        'target_danceability': 0.7,
        'max_tempo': 80
    },
    'sad': {
        'min_energy': 0.2,
        'target_danceability': 0.3,
        'max_tempo': 60
    },
    'intense': {
        'min_energy': 0.8,
        'target_danceability': 0.7,
        'min_tempo': 120
    },
    'cozy': {
        'min_energy': 0.5,
        'target_danceability': 0.6,
        'max_tempo': 80
    },
    'calm': {
        'min_energy': 0.3,
        'target_danceability': 0.4,
        'max_tempo': 50
    }
}

def analyze_tracks(description, track_ids):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    moods = { #maps a mood to a one of Open Weather's weather condtions
        'clear sky': 'happy',
        'few clouds': 'relax',
        'scattered clouds': 'chill',
        'broken clouds': 'melancholy',
        'shower rain': 'deep',
        'rain': 'sad',
        'thunderstorm': 'intense',
        'snow': 'cozy',
        'mist': 'calm'
    }


    mood = moods.get(description, 'mood')
    mood_params = mood_characteristics.get(mood, {})
    
    seed_tracks_param = ','.join(seed_tracks[:5])  # Spotify allows a maximum of 5 seed tracks

    query_params = {
        'seed_tracks': seed_tracks_param,
        'limit': 20,
        **mood_params  # Unpack the mood parameters into the query parameters
    }

    response = requests.get(
        "https://api.spotify.com/v1/recommendations",
        headers=headers,
        params=query_params


if __name__ == '__main__':
    lat, lon = get_lat_lon('Toronto', 'ON', 'CA', weather_api_key)
    print(get_weather(lat, lon, weather_api_key))



