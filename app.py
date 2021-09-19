import random
from flask import Flask, redirect, request, jsonify, render_template, g, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
from urllib.parse import urlparse
from conf import *
import util
from routes import route_blueprint
from api import api_blueprint
from auth import auth_blueprint
from dbutil import *

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static'
)
app.config['SECRET_KEY'] = appsecret

app.register_blueprint(route_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(auth_blueprint)

@app.before_request
def before_request():
    g.username = None
    g.displayname = None
    g.uid = 0
    g.loggedin = False
    g.count = 0
    if 'username' in session:
        g.username = session['username']
        g.displayname = session['displayname']
        g.loggedin = True
        g.uid = session['uid']
        g.count = getReqCount(g.uid)

####################
# Helper functions #
####################

import nightbot

if __name__ == '__main__':
    app.run(host='0.0.0.0')
