from app import app, db, addNewUser, getVideoId, findOrAddSong
import api
import routes
import random
from flask import Flask, url_for, redirect, request, jsonify, render_template, g, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
from enum import IntEnum
from urllib.parse import urlparse
import json
from dbconf import *
import requests

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

sloauth = oauth.remote_app('streamlabs',
                           base_url='https://streamlabs.com/api/v1.0/',
                           request_token_url=None,
                           access_token_method='POST',
                           access_token_url='https://streamlabs.com/api/v1.0/token',
                           authorize_url='https://www.streamlabs.com/api/v1.0/authorize',
                           consumer_key=slClientId,
                           consumer_secret=slSecret,
                           request_token_params={
                               'scope': ['donations.read', 'donations.create']}
                           )


@twitchoauth.tokengetter
def get_twitch_token(token=None):
    """
    Does what it says on the label.
    """
    return session.get('twitch_token')

    # API endpoint for adding a user

@sloauth.tokengetter
def get_sl_token():
    return session.get('access_token')    


@app.route('/adduser', methods=['POST', ])
def addUser():
    """
    Creates a new 'local' user in the table and logs them in.
    'username' - user's desired username
    'email' - user's email address
    'password' - user's chosen password. (Not stored plaintext!)
    """
    username = request.form['username']
    displayname = request.form['username']
    password = request.form['password']
    email = request.form['email']
    uid = addNewUser(username, bcrypt.generate_password_hash(
        password), email, displayname)
    session['username'] = username
    session['loggedIn'] = True
    session['uid'] = uid
    session['displayname'] = username
    return redirect(url_for('renderHome'))


@app.route('/api/v1/savepass', methods=['POST', ])
def savePass():
    """
    Saves a new password for the currently logged in user
    """
    if (session['uid'] == 0):
        return 'NO'  # You can't do this! I forbid it!
    if (request.json['password'] == ''):
        return 'MT'  # You can't do this! I forbid it!
    cursor = db.connection.cursor()
    pw = bcrypt.generate_password_hash(request.json['password'])
    query = 'UPDATE users SET password = %s WHERE uid = %s'
    cursor.execute(query, (pw, session['uid'],))
    return 'OK'  # Password set successfully


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
    query = 'SELECT username, password, uid, displayname FROM users WHERE username = %s OR email = %s'
    cursor.execute(query, [username, username, ])
    user = cursor.fetchone()
    if user['password'] == None or user['password'] == '':
        flash('Your account was created by logging in with Twitch. Try logging in there and changing your password in your profile settings, if you wish to log in with a username and password here.')
        return render_template('login.jinja')
    temp = user['password']
    if len(user) > 0:
        session.pop('username', None)
        if (bcrypt.check_password_hash(temp, password)) == True:
            session['username'] = user['username']
            session['displayname'] = user['displayname']
            session['loggedIn'] = True
            session['uid'] = user['uid']
            return redirect(url_for('renderHome'))
        else:
            flash('Invalid Username or Password')
            return render_template('login.jinja', username=g.username, loggedIn=g.loggedin)


@app.route('/sllink')
def sllink():
    """
    Endpoint for linking Streamlabs account to existing account.
    """
    return sloauth.authorize(callback=url_for('slauth', _external=True, _scheme=app.config['SCHEME'],))


@app.route('/slauth')
def slauth():
    """
    Callback endpoint for Streamlabs OAuth account linking.
    """
    if (session['uid'] == 0):
        return render_template('error.jinja', error=('You must be logged in to perform this action'))
    code = request.args['code']
    url = "https://streamlabs.com/api/v1.0/token"
    data= {
        'grant_type': 'authorization_code',
        'client_id': slClientId,
        'client_secret': slSecret,
        'redirect_uri': url_for('slauth', _external=True, _scheme=app.config['SCHEME'],),
        'code': code
    }
    r = requests.post(url, data=data)
    res = r.json()
    if ('access_token' in res and 'refresh_token' in res):
        session['slAccessToken'] = res['access_token']
        session['slRefreshToken'] = res['refresh_token']
    else:
        # Error out - we couldn't get a token for whatever reason
        return render_template('error.jinja', error=('You must be logged in to perform this action'))


    print(res)

@app.route('/slok')
def slok():
    print('1')


#       {
#      "streamlabs":{
#         "id":3929217,
#         "display_name":"sunnyding602"
#      },
#      "twitch":{
#         "id":124287875,
#         "display_name":"sunnyding602",
#         "name":"sunnyding602"
#      },
#      "youtube":{
#         "id":"UCuDKXjZv4B3F58xv_76gw",
#         "title":"runxi@streamlabs.com"
#      },
#      "mixer":{
#         "id":10969035,
#         "name":"Flyfurrysnail"
#      },
#      "facebook":{
#         "id":"1520473641329778",
#         "name":"Sunny Ding"
#      }
#   }
#     twitchclient = TwitchHelix(
#         client_id=twitchClientId, oauth_token=resp['access_token'])
#     twitchuser = twitchclient.get_users()
#     twitchuid = twitchuser[0]['id']
#     twitchname = twitchuser[0]['display_name']
#     # Set the current user's tuid
#     cursor = db.connection.cursor()
#     query = 'UPDATE users SET tuid = %s, twitchname = %s WHERE uid = %s'
#     cursor.execute(query, [twitchuid, twitchname, session['uid']])
#     query = 'SELECT * FROM users WHERE uid = %s'
#     cursor.execute(query, (session['uid'],))
#     row = cursor.fetchone()
#     session['uid'] = row['uid']
#     session['loggedIn'] = True
#     session['username'] = row['username']
#     session['displayname'] = row['displayname']
#     session['tuid'] = twitchuid
#     session['twitchname'] = twitchname
#     return redirect(url_for('editProfile'))




@app.route('/tlink')
def twitchlink():
    """
    Endpoint for linking Twitch account to existing account.
    """
    return twitchoauth.authorize(callback=url_for('tlinkok', _external=True, _scheme=app.config['SCHEME'],))


@app.route('/tunlink')
def twitchunlink():
    """
    Endpoint for unlinking your Twitch account from existing account
    # NOTE: You need to enforce setting a password here!
    """
    cursor = db.connection.cursor()
    query = 'SELECT password FROM users WHERE uid = %s'
    cursor.execute(query, (session['uid'],))
    pw = cursor.fetchone()['password']
    if (pw == ''):
        return render_template('error.jinja', error=('You must set a password for your account first'))
    query = 'UPDATE users SET tuid = 0, tname = "" WHERE uid = %s'
    cursor.execute(query, (session['uid'],))
    session['tuid'] = 0
    session['tname'] = ''
    return redirect(url_for('editProfile'))


@app.route('/tlinkok')
def tlinkok():
    """
    Callback endpoint for Twitch OAuth login.
    Creates new user if necessary and logs them in.
    """
    if (session['uid'] == 0):
        return render_template('error.jinja', error=('You must be logged in to perform this action'))
    resp = twitchoauth.authorized_response()
    if resp is None:
        return render_template('error.jinja', error=('Error linking account: ' + request.args['error'] + ' - ' + request.args['error_description']))
    twitchclient = TwitchHelix(
        client_id=twitchClientId, oauth_token=resp['access_token'])
    twitchuser = twitchclient.get_users()
    twitchuid = twitchuser[0]['id']
    tname = twitchuser[0]['display_name']
    # Set the current user's tuid
    cursor = db.connection.cursor()
    query = 'UPDATE users SET tuid = %s, tname = %s WHERE uid = %s'
    cursor.execute(query, [twitchuid, tname, session['uid']])
    query = 'SELECT * FROM users WHERE uid = %s'
    cursor.execute(query, (session['uid'],))
    row = cursor.fetchone()
    session['uid'] = row['uid']
    session['loggedIn'] = True
    session['username'] = row['username']
    session['displayname'] = row['displayname']
    session['tuid'] = twitchuid
    session['tname'] = tname
    return redirect(url_for('editProfile'))


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
    query = 'SELECT * FROM users WHERE tuid = %s'
    cursor.execute(query, [twitchuid, ])
    row = cursor.fetchone()
    if row is None:
        uid = addNewUser(username, '', email, -1, twitchuid)
        query = 'SELECT * FROM users WHERE uid = %s'
        cursor.execute(query, (uid,))
        row = cursor.fetchone()
    # Set the session whatsits and let's rock!
    session['uid'] = row['uid']
    session['loggedIn'] = True
    session['username'] = row['username']
    session['displayname'] = row['displayname']
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
    g.displayname = None
    g.tuid = 0
    g.tname = ''
    return render_template('home.jinja')
