from flask import Flask, Blueprint, render_template, redirect, request, jsonify, session
from dotenv import load_dotenv
import requests
from datetime import datetime
import os
import urllib.parse

load_dotenv()

core = Blueprint('core', __name__)

@core.route('/')
def index():
    if 'access_token' not in session:
        return render_template("index.html")
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    

    headers = {
    'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(os.getenv("API_BASE_URL") + 'me', headers=headers)
    user_info = response.json()
    response = requests.get(os.getenv("API_BASE_URL") + 'me', headers=headers)
    return render_template("profile.html", profile_info=user_info,
            username = user_info["display_name"], 
            country = user_info["country"], 
            followers = user_info["followers"]['total'],
            user_id = user_info['id'],
            logged = True)

@core.route('about')
def info():
    return render_template('info.html')

