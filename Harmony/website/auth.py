from flask import Flask, Blueprint, render_template, redirect, request, jsonify, session
from dotenv import load_dotenv
import requests
from datetime import datetime
import os
import urllib.parse

load_dotenv()

auth = Blueprint('auth', __name__)
@auth.route('/login')
def login():
    print("lol")
    params = {
        'client_id' : os.getenv('CLIENT_ID'),
        'response_type' : 'code',
        'scope': 'user-read-private user-read-email playlist-read-private user-top-read playlist-modify-public playlist-read-private playlist-modify-private ',  
        'redirect_uri' : os.getenv('REDIRECT_URI'),
        'show_dialog' : False

        #Access token is given once they log in, so they don't have to log in everytime
        }
    auth_url = f"{os.getenv('AUTH_URL')}?{urllib.parse.urlencode(params)}"
    #Get request must be made to an authorization URL, params must be parsed. URLib encodes the params 
    return redirect(auth_url)

#Make request to Spotify API

@auth.route('/callback/')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    if 'code' in request.args:
        req = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': os.getenv('REDIRECT_URI'),
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET')
        }
        token_url = os.getenv("TOKEN_URL")
        response = requests.post(token_url, data=req)
        if response.status_code != 200:
            print("Failed to fetch access token")
            return jsonify({"error": "Failed to fetch access token."})

        token_info = response.json()
        print("Token Info:", token_info)
        session['access_token'] = token_info.get('access_token')
        session['refresh_token'] = token_info.get('refresh_token')
        session['expires_at'] = datetime.now().timestamp() + token_info.get('expires_in', 3600)

        # Redirect to the homepage after successful login
        return redirect('/')

    return jsonify({"error": "Invalid request. No code provided."})


    
@auth.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization' : f"Bearer {session['access_token']}"

    }

    response = requests.get(os.getenv("API_BASE_URL") + '/me/', headers=headers)
    ##stores result of making a request 

    playlists = response.json()
    return jsonify(playlists) # returns playlists to user

@auth.route('/refresh-token')
def refresh_token(): 
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        req_body = {  #parameters Spotify requires to gain a new access token
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': os.getenv("CLIENT_ID"),
            'client_secret': os.getenv("CLIENT_SECRET"),
        }
        response = requests.post("https://accounts.spotify.com/api/token/", data=req_body)   
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token'] #makes the new token the access token
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in'] #gets current time and adds seconds until token expires
        return redirect('/')
    
@auth.route('/profile')
def get_user(): 
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization' : f"Bearer {session['access_token']}"

    }
    response = requests.get(os.getenv("API_BASE_URL") + '/me/', headers=headers)
    profile_info = {
        'display_name': response.json().get('display_name'),
        'email': response.json().get('email'),
        'country': response.json().get('country'),
        'followers': response.json().get('followers'),
        'id': response.json().get('id'),
        'photo': response.json().get('url')
    }

    return render_template('profile.html', profile_info=profile_info)

@auth.route('/artists')
def artists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    limit = 10  # Limit to 10 artists
    response = requests.get(os.getenv("API_BASE_URL") + f'me/top/artists?limit={limit}', headers=headers)
    
    
    if response.status_code != 200:
        print(f"Error fetching top artists: {response.json()}")  # Additional error logging
        return redirect('/login')

    fav_artists = response.json()
    return render_template('fav_artists.html', top_artists=fav_artists["items"])

@auth.route('/toptracks')
def toptracks(): 
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    limit = 10
    response = requests.get(os.getenv("API_BASE_URL") + f'me/top/tracks?limit={limit}', headers=headers)
    if response.status_code != 200:
        print(f"Error fetching top tracks: {response.json()}")  # Additional error logging
        return redirect('/login')
    
    top_tracks = response.json()
    print("Top tracks:", top_tracks)  # Debugging statement

    return render_template('top_tracks.html', top_tracks = top_tracks["items"])

@auth.route('/relatedartists')
def get_related_artists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    limit = 10
    top_artists_response = requests.get(os.getenv("API_BASE_URL") + f'me/top/artists?limit={limit}', headers=headers)
    if top_artists_response.status_code != 200:
        print(f"Error fetching top artists: {top_artists_response.json()}")
        return redirect('/login')

    top_artists = top_artists_response.json()["items"]
    
    related_artists = []
    for artist in top_artists:
        artist_id = artist['id']
        response = requests.get(os.getenv("API_BASE_URL") + f'artists/{artist_id}/related-artists', headers=headers)
        if response.status_code == 200:
            related_artists.extend(response.json()["artists"])

    return render_template('related_artists.html', related_artists=related_artists)
