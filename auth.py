from flask import Blueprint, url_for, redirect, request, render_template, g, session, flash
import bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
import json
from conf import *
import requests
from dbutil import *


auth_blueprint = Blueprint('auth_blueprint', __name__)

oauth = OAuth()

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

@sloauth.tokengetter
def get_sl_token():
    return session.get('access_token')


@auth_blueprint.route('/adduser', methods=['POST', ])
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
    uid = addNewUser(username=username,
                     password=bcrypt.generate_password_hash(password),
                     email=email,
                     displayname=username)
    session['username'] = username
    session['loggedIn'] = True
    session['uid'] = uid
    session['displayname'] = username
    return redirect(url_for('route_blueprint.renderHome'))


@auth_blueprint.route('/api/v1/savepass', methods=['POST', ])
def savePass():
    """
    Saves a new password for the currently logged in user
    """
    if (session['uid'] == 0):
        return 'NO'  # You can't do this! I forbid it!
    if (request.json['password'] == ''):
        return 'MT'  # You can't do this! I forbid it!
    pw = bcrypt.generate_password_hash(request.json['password'])
    result = setUserPassword(session['uid'], pw)
    if (result == 1):
        return 'OK'  # Password set successfully
    return 'NG'  # Something bad happened!


@auth_blueprint.route('/authenticate', methods=['POST', ])
def authenticate():
    """
    Attempts to authenticate a user.
    Indicates and redirects if user's account is not a 'native' one (i.e., OAuth created).
    'username' - *EITHER* a username or an email address, checks both.
    'password' - Well, y'know.
    """
    username = request.form['username']
    password = request.form['password']
    user = getLoginUser(username)
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
            return redirect(url_for('route_blueprint.renderHome'))
        else:
            flash('Invalid Username or Password')
            return render_template('login.jinja', username=g.username, loggedIn=g.loggedin)


@auth_blueprint.route('/sllink')
def sllink():
    """
    Endpoint for linking Streamlabs account to existing account.
    """
    return sloauth.authorize(callback=url_for('slauth', _external=True, _scheme=app.config['SCHEME'],))


@auth_blueprint.route('/slauth')
def slauth():
    """
    Callback endpoint for Streamlabs OAuth account linking.
    """
    code = request.args['code']
    url = "https://streamlabs.com/api/v1.0/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': slClientId,
        'client_secret': slSecret,
        'redirect_uri': url_for('slauth', _external=True, _scheme=app.config['SCHEME'],),
        'code': code
    }
    r = requests.post(url, data=data)
    res = r.json()
    if ('access_token' in res and 'refresh_token' in res):
        # Get the user info with this token
        sltoken = res['access_token']
        refresh_token = res['refresh_token']
        url = "https://streamlabs.com/api/v1.0/user?access_token=" + sltoken
        headers = {"Accept": "application/json"}
        response = requests.request("GET", url, headers=headers)
        userR = response.json()
        sluid = userR['streamlabs']['id']
        slname = userR['streamlabs']['display_name']
        # Do we ADD the user, or UPDATE them?
        if (session['uid'] == 0):
            row = getStreamlabsUser(sluid)
            if row is None:
                uid = addNewUser(username=slname,
                                 password='',
                                 email='',
                                 displayname=slname,
                                 uid=-1,
                                 sluid=sluid,
                                 slname=slname,
                                 sltoken=sltoken)
                row = getUserInfo(uid)
            # Set the session whatsits and let's rock!
            session['uid'] = row['uid']
            session['loggedIn'] = True
            session['username'] = row['username']
            session['displayname'] = row['displayname']
        else:
            setSLUIDForUser(sluid, slname, session['uid'])
        session['sltoken'] = sltoken
        return redirect(url_for('route_blueprint.editProfile'))


@auth_blueprint.route('/tlink')
def twitchlink():
    """
    Endpoint for linking Twitch account to existing account.
    """
    return twitchoauth.authorize(callback=url_for('tlinkok', _external=True, _scheme=app.config['SCHEME'],))


@auth_blueprint.route('/tunlink')
def twitchunlink():
    """
    Endpoint for unlinking your Twitch account from existing account
    """
    pw = getPasswordForUser(session['uid'])
    if (pw == ''):
        return render_template('error.jinja', error=('You must set a password for your account first'))
    unlinkTwitch(session['uid'])
    # TODO: Handle errors on unlinking
    session['tuid'] = 0
    session['tname'] = ''
    return redirect(url_for('route_blueprint.editProfile'))


@auth_blueprint.route('/slunlink')
def slunlink():
    """
    Endpoint for unlinking your Streamlabs account from existing account
    """
    pw = getPasswordForUser(session['uid'])
    if (pw == ''):
        return render_template('error.jinja', error=('You must set a password for your account first'))
    unlinkStreamlabs(session['uid'])
    session['sluid'] = 0
    session['slname'] = ''
    return redirect(url_for('route_blueprint.editProfile'))


@auth_blueprint.route('/tlinkok')
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
    res = setTUIDForUser(twitchuid, tname, session['uid'])
    if (res == 1):
        row = getUserInfo(session['uid'])
        session['uid'] = row['uid']
        session['loggedIn'] = True
        session['username'] = row['username']
        session['displayname'] = row['displayname']
        session['tuid'] = twitchuid
        session['tname'] = tname
        return redirect(url_for('route_blueprint.editProfile'))
    return render_template('error.jinja', error=('Error linking account: ' + request.args['error'] + ' - ' + request.args['error_description']))


@auth_blueprint.route('/tlogin')
def login():
    """
    Endpoint for logging in with Twitch OAuth.
    """
    return twitchoauth.authorize(callback=url_for('auth_blueprint.authorized', _external=True, _scheme=scheme,))


@auth_blueprint.route('/tlogin/authorized')
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
    row = getTwitchUser(twitchuid)
    if row is None:
        uid = addNewUser(username=username,
                         password='',
                         email=email,
                         displayname=username,
                         uid=-1,
                         tuid=twitchuid,
                         tname=username)
        row = getUserInfo(session['uid'])
    # Set the session whatsits and let's rock!
    session['uid'] = row['uid']
    session['loggedIn'] = True
    session['username'] = row['username']
    session['displayname'] = row['displayname']
    return redirect(url_for('route_blueprint.renderHome'))


@auth_blueprint.route('/logout')
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
