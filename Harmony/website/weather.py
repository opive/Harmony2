import requests
from flask import Flask, Blueprint, render_template, request, redirect, session, jsonify
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

mood_characteristics = { #uses Spotify's parameters for songs to further narrow down a song to a mood
    'happy': {
        'min_energy': 0.7,
        'target_danceability': 0.8,
        'min_tempo': 100,
        'min_valence': 0.8
    },
    'relax': {
        'min_energy': 0.4,
        'target_danceability': 0.5,
        'min_tempo': 70,
        'min_valence': 0.3,
        'max_valence': 0.7
    },
    'chill': {
        'min_energy': 0.3,
        'target_danceability': 0.6,
        'min_tempo': 70,
        'min_valence': 0.4,
        'max_valence': 0.7
    },
    'melancholy': {
        'min_energy': 0.3,
        'target_danceability': 0.4,
        'max_tempo': 80,
        'min_valence': 0.1,
        'max_valence': 0.4
    },
    'deep': {
        'min_energy': 0.6,
        'target_danceability': 0.7,
        'max_tempo': 80,
        'min_valence': 0.2,
        'max_valence': 0.5
    },
    'sad': {
        'min_energy': 0.2,
        'target_danceability': 0.3,
        'max_tempo': 60,
        'min_valence': 0.1,
        'max_valence': 0.3
    },
    'intense': {
        'min_energy': 0.8,
        'target_danceability': 0.7,
        'min_tempo': 120,
        'min_valence': 0.5,
        'max_valence': 0.8
    },
    'cozy': {
        'min_energy': 0.5,
        'target_danceability': 0.6,
        'max_tempo': 80,
        'min_valence': 0.4,
        'max_valence': 0.7
    },
    'calm': {
        'min_energy': 0.3,
        'target_danceability': 0.4,
        'max_tempo': 50,
        'min_valence': 0.3,
        'max_valence': 0.6
    }
}

def get_user_id(): 
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization' : f"Bearer {session['access_token']}"
    }
    response = requests.get(os.getenv("API_BASE_URL") + '/me/', headers=headers)
    return response.json().get('id')

def get_top_genres():
    token = session.get('access_token')
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {token}"
    }

    response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)
    if response.status_code == 200:
        top_tracks = response.json().get('items')

        track_ids = []
        for track in top_tracks:
            track_ids.append(track['id'])

        genres = set()
        for track in top_tracks:
            for artist in track['artists']:
                artist_response = requests.get(f"https://api.spotify.com/v1/artists/{artist['id']}", headers=headers)
                if artist_response.status_code == 200:
                    genres.update(artist_response.json().get('genres'))

        return track_ids, list(genres)


def get_user_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
    if response.status_code == 200:
        playlists = response.json().get('items', [])
        playlist_ids = []
        for playlist in playlists:
            playlist_ids.append(playlist['id'])
        return playlist_ids

def get_track_ids(playlist_ids):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = { #headers include the access token for spotify to identify
        'Authorization' : f"Bearer {session['access_token']}"

    }
    track_ids = []
    for playlist_id in playlist_ids:
        response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
        if response.status_code == 200:
            tracks = response.json().get('items', [])
            for track in tracks:
                if track['track']:
                    track_ids.append(track['track']['id'])
    return track_ids

def audio_features(track_ids): 
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    audio_features = []
    for i in range(0, len(track_ids), 100):  # Spotify API limit is 100 tracks per request, iterates over the track_ids list in chunks of 100 at a time
        ids = ','.join(track_ids[i:i+100])
        response = requests.get(f'https://api.spotify.com/v1/audio-features?ids={ids}', headers=headers)
        if response.status_code == 200:
            audio_features.extend(response.json().get('audio_features', []))
        return audio_features

def filter_tracks(audio_features, mood):
    mood_params = mood_characteristics.get(mood, {})
    filtered_track_ids = []
    for track in audio_features:
        if track and (mood_params.get('min_energy', 0) <= track['energy'] <= mood_params.get('max_energy', 1)) and \
           (mood_params.get('target_danceability', 0) - 0.1 <= track['danceability'] <= mood_params.get('target_danceability', 1) + 0.1) and \
           (mood_params.get('min_tempo', 0) <= track['tempo'] <= mood_params.get('max_tempo', 500)) and \
           (mood_params.get('min_valence', 0) <= track['valence'] <= mood_params.get('max_valence', 1)):
            filtered_track_ids.append(track['id'])
    return filtered_track_ids


def get_recommendations(filtered_tracks, genres, mood_params):

    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    seed_tracks_param = ','.join(filtered_tracks[:5])  # Spotify allows a maximum of 5 seed tracks
    genre_param = ','.join(genres[:5])  # Limit genres to 5
    
    query_params = { #dictionary of query parameters for the API request, 
        'seed_tracks': seed_tracks_param,
        'seed_genres': genre_param,
        'limit': 20, 
        **mood_params
    }

    response = requests.get("https://api.spotify.com/v1/recommendations", headers=headers, params=query_params)
    if response.status_code == 200:
        return response.json().get('tracks', [])
    return []


def create_playlist(user_id, track_ids, ):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    req_body = {
        'name' : "Playlist of the day",
        'description': 'This was created by Harmony based on the weather in your area',
        'public': True
    }
    response = requests.get("https://api.spotify.com/v1/recommendations", headers=headers, req_body = req_body)
    if response.status_code == 201:
        playlist_id = response.json().get('id')
        track_uris = []
        for track_id in track_ids:
            track_uri = f'spotify:track:{track_id}'
            track_uris.append(track_uri)
        
        response_tracks = requests.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers, json={'uris': track_uris})
        if response_tracks.status_code == 201:
                return playlist_id

        
        



def get_playlist(description):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    genres = get_top_genres()
    mood = moods.get(description)
    mood_params = mood_characteristics.get(mood)

    playlist_ids = get_user_playlists()
    all_track_ids = get_track_ids(playlist_ids)
    audio_features = audio_features(all_track_ids)
    filtered_tracks = filter_tracks(audio_features, mood, genres)
    recommended_tracks = get_recommendations(filtered_tracks, genres, mood_params)

    combined_track_ids = filtered_tracks + [track['id'] for track in recommended_tracks]

    user_info_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    user_id = user_info_response.json().get('id')
    playlist_id = create_playlist(user_id, 'Today\'s Playlist', 'A custom playlist based on weather and your taste.', combined_track_ids)
    
    return playlist_id


def return_playlist():
    if 'access_token' not in session:
        return redirect('/login')
    
    description = request.form.get('description')
    
    playlist_id = get_playlist(description)
    return jsonify({'playlist_id': playlist_id}), 200





