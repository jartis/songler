import random
from flask import Flask, url_for, redirect, request, jsonify, render_template, g, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
from urllib.parse import urlparse
from dbconf import *
import util

app = Flask(
    __name__,
    static_url_path='',
    static_folder='static'
)

#app.config['DEBUG'] = True
app.config['SECRET_KEY'] = appsecret
app.config['MYSQL_HOST'] = dbhost
app.config['MYSQL_USER'] = dbuser
app.config['MYSQL_PORT'] = dbport
app.config['MYSQL_PASSWORD'] = dbpass
app.config['MYSQL_DB'] = dbname
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# For Twitch OAuth redirects (and testing)
app.config['SCHEME'] = 'http'
db = MySQL(app)


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


def addNewUser(username, password, email, displayname, uid=-1, tuid='', tname='', sluid='', slname=''):
    """
    Adds a new user entry to the database.
    <username>: Desired username for new account.
    <password>: Password for new account. Blank if created with an OAuth provider.
    <email>: Email account to attach to new user. Populated from OAuth provider if possible.
    <uid>: Defaults to -1. If provided, sets UID in DB, if -1, use the Auto-Increment.
    <tuid>: Twitch UID, if account was created with Twitch OAuth.
    """
    cursor = db.connection.cursor()
    if tuid != '':
        # Create a Twitch-based user
        query = 'INSERT INTO users (username, password, email, tuid, tname, signup, displayname) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password,
                       email, tuid, tname, username))
    elif sluid != '':
        query = 'INSERT INTO users (username, password, email, sluid, slname, signup, displayname) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password,
                       email, sluid, slname, username))
    else:
        # Create a Username/Password user
        query = 'INSERT INTO users (username, password, email, signup, displayname) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password, email, displayname))
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    return int(row['uid'])





import auth
import routes
import api
import nightbot
from dbutil import *

if __name__ == '__main__':
    app.run(host='0.0.0.0')
