import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

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




app.register_blueprint(core, url_prefix='/')
app.register_blueprint(error_pages)


from .import models



