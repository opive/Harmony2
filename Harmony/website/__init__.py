import os
from flask import Flask, render_template

app = Flask(__name__)

app.config['SECRET_KEY'] = 'peepeepoopoopeepeepoopoo'


from website.core.views import core
from website.error_pages.handlers import error_pages
from website.auth import auth
from website.weather import weather


app.register_blueprint(core, url_prefix='/')
app.register_blueprint(error_pages)
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(weather, url_prefix='/')





