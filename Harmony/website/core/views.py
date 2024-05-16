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
    
    if 'access_token' in session:
        headers = {
        'Authorization': f"Bearer {session['access_token']}"
        }
        response = requests.get(os.getenv("API_BASE_URL") + 'me', headers=headers)
        print(os.getenv("API_BASE_URL") + 'me/')
        userInfo = response.json()
        response = requests.get(os.getenv("API_BASE_URL") + 'me', headers=headers)
        return render_template("profile.html", 
                        username = userInfo["display_name"], 
                        country = userInfo["country"], 
                        followers = userInfo["followers"]['total'],
                        logged = True)

@core.route('about')
def info():
    return render_template('info.html')


