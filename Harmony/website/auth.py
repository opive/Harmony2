from flask import Flask, Blueprint, render_template, redirect, request, jsonify, session
from dotenv import load_dotenv
import requests
from datetime import datetime
import env
import os
import urllib.parse

load_dotenv()

auth = Blueprint('auth', __name__)
@auth.route('/login')
def login():
    params = {
        'client_id' : os.getenv('CLIENT_ID'),
        'response_type' : 'code',
        'scope' : 'scope',
        'redirect_uri' : os.getenv('REDIRECT_URI'),
        'show_dialogue' : True

        #Access token is given once they login, so they don't have to log in everytime
        }

    auth_url = f"{os.getenv('AUTH_URL')}?{urllib.parse.urlencode(params)}"
    #Get request must be made to an authorization URL, params must be parsed. URLib encodes the params 
    return redirect(auth_url)

#Make request to Spotify API

@auth.route('/callback')
def callback(): 
    if 'error' in request.args:
        print("you're cooked")
        return jsonify({"error": request.args['error']})
    #returns error if something is wrong with the user's account

    if 'code' in request.args: #build a request that contains data to send
        print("you cooked")
        req = {
            'code' : request.args['code'],
            'grant_type' : 'authorization_code',
            'redirect_uri': os.getenv("REDIRECT_URI"),
            'client_id': os.getenv("CLIENT_ID"),
            'client_secret': os.getenv("CLIENT_SECRET"),
        }
        response = request.post("TOKEN_URL", data=req) #send token url for access token
        token_info = response.json() #spotify will give back token info as a json object

        session['access_token'] = token_info = ['access_token']
        session['refresh_token'] = token_info =['refresh_token'] #refreshes access token
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in'] #gets current time and adds seconds until token expires

    
        return redirect('/playlists')
    
@auth.route('playlists')
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
        response = request.post(os.getenv("TOKEN_URL"), data=req_body)   
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token'] #makes the new token the access token
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in'] #gets current time and adds seconds until token expires
        return redirect('/playlists')