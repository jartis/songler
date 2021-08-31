from app import app, db, addNewUser, getVideoId, findOrAddSong
import api
import render
import random
from flask import Flask, url_for, redirect, request, jsonify, render_template, g, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
from enum import IntEnum
from urllib.parse import urlparse
from dbconf import *

oauth = OAuth()
bcrypt = Bcrypt(app)

twitchoauth = oauth.remote_app('twitch',
                               base_url='https://api.twitch.tv/kraken/',
                               request_token_url=None,
                               access_token_method='POST',
                               access_token_url='https://api.twitch.tv/kraken/oauth2/token',
                               authorize_url='https://api.twitch.tv/kraken/oauth2/authorize',
                               consumer_key=twitchClientId,
                               consumer_secret=twitchSecret,
                               request_token_params={'scope': ["user_read"]}
                               )

twitchclient = TwitchClient(client_id=twitchClientId)

@twitchoauth.tokengetter
def get_twitch_token(token=None):
    """
    Does what it says on the label.
    """
    return session.get('twitch_token')

    # API endpoint for adding a user
@app.route('/adduser', methods=['POST', ])
def addUser():
    """
    Creates a new 'local' user in the table and logs them in.
    'username' - user's desired username
    'email' - user's email address
    'password' - user's chosen password. (Not stored plaintext!)
    """
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    uid = addNewUser(username, bcrypt.generate_password_hash(password), email)
    session['username'] = username
    session['loggedIn'] = True
    session['uid'] = uid
    return redirect(url_for('renderHome'))


@app.route('/authenticate', methods=['POST', ])
def authenticate():
    """
    Attempts to authenticate a user.
    Indicates and redirects if user's account is not a 'native' one (i.e., OAuth created).
    'username' - *EITHER* a username or an email address, checks both.
    'password' - Well, y'know.
    """
    username = request.form['username']
    password = request.form['password']
    cursor = db.connection.cursor()
    query = 'SELECT username, password, uid FROM users WHERE username = %s OR email = %s'
    cursor.execute(query, [username, username, ])
    user = cursor.fetchone()
    if user['password'] == '':
        flash('Your account was created by logging in with Twitch. Try logging in there and changing your password in your profile settings, if you wish to log in with a username and password here.')
        return render_template('login.jinja', username=g.username, loggedIn=g.loggedin)
    temp = user['password']
    if len(user) > 0:
        session.pop('username', None)
        if (bcrypt.check_password_hash(temp, password)) == True:
            session['username'] = request.form['username']
            session['loggedIn'] = True
            session['uid'] = user['uid']
            return redirect(url_for('renderHome'))
        else:
            flash('Invalid Username or Password')
            return render_template('login.jinja', username=g.username, loggedIn=g.loggedin)


@app.route('/tlogin')
def login():
    """
    Endpoint for logging in with Twitch OAuth.
    """
    return twitchoauth.authorize(callback=url_for('authorized', _external=True, _scheme=app.config['SCHEME'],))


@app.route('/tlogin/authorized')
def authorized():
    """
    Callback endpoint for Twitch OAuth login.
    Creates new user if necessary and logs them in.
    """
    resp = twitchoauth.authorized_response()
    if resp is None:
        return render_template('error.jinja', error=('Error logging in: ' + request.args['error'] + ' - ' + request.args['error_description']))
    twitchclient = TwitchHelix(
        client_id=twitchClientId, oauth_token=resp['access_token'])
    twitchuser = twitchclient.get_users()
    username = twitchuser[0]['display_name']
    twitchuid = twitchuser[0]['id']
    email = twitchuser[0]['email']
    # Okay, if this user doesn't exist in our database yet, let's add them!
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM users WHERE twitch = %s'
    cursor.execute(query, [twitchuid, ])
    row = cursor.fetchone()
    if row is None:
        uid = addNewUser(username, '', email, -1, twitchuid)
    else:
        uid = row['uid']
    # Set the session whatsits and let's rock!
    session['uid'] = uid
    session['loggedIn'] = True
    session['username'] = username
    return redirect(url_for('renderHome'))


@app.route('/logout')
def logout():
    """
    Clears the session and logs out.
    """
    session.pop('twitch_token', None)
    session.clear()
    g.username = None
    g.uid = None
    g.loggedin = False
    return render_template('home.jinja')