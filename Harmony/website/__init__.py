import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SECRET_KEY'] = 'peepeepoopoopeepeepoopoo'

#database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
#

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

 
#Blueprints

from website.core.views import core
from website.error_pages.handlers import error_pages
from website.auth import auth
# from website.weather import weather


app.register_blueprint(core, url_prefix='/')
app.register_blueprint(error_pages)
app.register_blueprint(auth, url_prefix='/')
# app.register_blueprint(weather, url_prefix='/')

from .import models



