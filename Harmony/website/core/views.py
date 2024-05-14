import os
from flask import Flask, render_template, request, Blueprint, redirect, session
import requests
import datetime

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
    print(os.getenv("API_BASE_URL") + 'me/')
    userInfo = response.json()
    response = requests.get(os.getenv("API_BASE_URL") + 'me', headers=headers)
    
    return render_template("main_logged_in.html", 
                        username = userInfo["display_name"], 
                        country = userInfo["country"], 
                        followers = userInfo["followers"]['total'],
                        logged = True)

@core.route('about')
def info():
    return render_template('info.html')

# @core.route('login')
# def login():
#     # return render_template()
