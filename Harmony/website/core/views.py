from flask import Flask, render_template, request, Blueprint

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return render_template('index.html')


@core.route('about')
def info():
    return render_template('info.html')

@core.route('login')
def login():
    return render_template('login.html')