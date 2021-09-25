from flask import Flask, redirect, request, jsonify, render_template, g, session, flash

from conf import *
from util import *
from dbutil import *
from routes import route_blueprint
from api import api_blueprint
from auth import auth_blueprint
from nightbot import nb_blueprint

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static'
)
app.config['SECRET_KEY'] = appsecret

app.register_blueprint(route_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(nb_blueprint)


@app.before_request
def before_request():
    g.ver = VER
    g.username = None
    g.displayname = None
    g.uid = 0
    g.loggedin = False
    g.count = 0
    g.online = False
    if 'username' in session:
        g.username = session['username']
        g.displayname = session['displayname']
        g.loggedin = True
        g.uid = session['uid']
        g.count = getReqCount(g.uid)
        g.online = (getOnline(g.uid) == '1')

####################
# Helper functions #
####################


if __name__ == '__main__':
    app.run(host='0.0.0.0')
