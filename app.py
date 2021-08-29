import random
from flask import Flask, url_for, redirect, request, jsonify, render_template, g, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
from enum import IntEnum
from urllib.parse import urlparse

from dbconf import *


class authProvider(IntEnum):
    TWITCH = 1


app = Flask(
    __name__,
    static_url_path='',
    static_folder='static'
)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = appsecret
app.config['MYSQL_HOST'] = dbhost
app.config['MYSQL_USER'] = dbuser
app.config['MYSQL_PORT'] = dbport
app.config['MYSQL_PASSWORD'] = dbpass
app.config['MYSQL_DB'] = dbname
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

db = MySQL(app)
bcrypt = Bcrypt(app)
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

#############
# SeCuRiTy! #
#############


@app.before_request
def before_request():
    g.username = None
    g.uid = 0
    g.loggedin = False
    if 'username' in session:
        g.username = session['username']
        g.loggedin = True
        g.uid = session['uid']


@twitchoauth.tokengetter
def get_twitch_token(token=None):
    return session.get('twitch_token')

######################
# Template Rendering #
######################

# Login page


@app.route('/login')
def renderLogin():
    return render_template('login.jinja')

# Create user page


@app.route('/newuser')
def newuser():
    return render_template('newuser.jinja')

# User's overlay


@app.route('/wheel')
def renderWheel():
    if g.uid is None:
        return render_template('error.jinja', error=("You must be logged in to view your overlay"))
    return render_template('wheel.jinja', uid=g.uid, username=g.username, loggedIn=g.loggedin)

# Main page


@app.route('/')
@app.route('/home')
def renderHome():
    return render_template('home.jinja', username=g.username, loggedIn=g.loggedin)

# Public songlist for user


@app.route('/songlist/<user>', methods=['GET', ])
def showSongList(user):
    user = str(user)
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, [user, ])
    row = cursor.fetchone()
    if row is not None:
        uid = int(row['uid'])
        return render_template('requestlist.jinja', uid=g.uid, listuid=uid, listuser=user, username=g.username, loggedIn=g.loggedin)
    else:
        return render_template('error.jinja', error=("No user found with the name " + user), username=g.username, loggedIn=g.loggedin)

# Manage current user's songlist


@app.route('/managelist', methods=['GET', ])
def manageSongList():
    if int(g.uid) > 0:
        return render_template('managelist.jinja', uid=g.uid, username=g.username, loggedIn=g.loggedin)
    else:
        return render_template('error.jinja', error=("No songlist found for user " + g.username), username=g.username, loggedIn=g.loggedin)


#########################
# Authentication / User #
#########################

# API endpoint for adding a user
@app.route('/adduser', methods=['POST', ])
def addUser():
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
    return twitchoauth.authorize(callback=url_for('authorized', _external=True))


@app.route('/tlogin/authorized')
def authorized():
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
    session.pop('twitch_token', None)
    session.clear()
    g.username = None
    g.uid = None
    g.loggedin = False
    return render_template('home.jinja')

####################
# Actual API calls #
####################


@app.route('/api/v1/checkuser/<user>', methods=['GET', ])
def checkuser(user):
    user = str(user).replace('%', '\%').replace('_', '\_')
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, [user, ])
    row = cursor.fetchone()
    if row is not None:
        return '1'
    return '0'


@app.route('/api/v1/checkemail/<email>', methods=['GET', ])
def checkemail(email):
    email = str(email).replace('%', '\%').replace('_', '\_')
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM users WHERE email LIKE %s'
    cursor.execute(query, [email, ])
    row = cursor.fetchone()
    if row is not None:
        return '1'
    return '0'

# 'uid' is the user to get the song(list) for
# Sorts on plays/lastplayed by default


@app.route('/api/v1/allsongs/<uid>', methods=['GET'])
def getAllUserSongs(uid):
    uid = int(uid)
    cursor = db.connection.cursor()
    query = 'SELECT songlists.slid, artists.artist, titles.title, songlists.public, songlists.plays, '
    query += 'songlists.uid, songlists.lastplayed FROM songlists '
    query += 'INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid '
    query += 'WHERE uid = %s ORDER BY plays ASC, lastplayed ASC'
    cursor.execute(query, (uid,))
    result = cursor.fetchall()
    return jsonify(result)

# 'list' is a comma separated list of song ids to exclude
# 'uid' is the userid for the songs to pull
# 'count' is the number of songs to return
# Sorts by last played date, never and oldest first


@app.route('/api/v1/more', methods=['GET'])
def refillUserSongs():
    if 'list' not in request.args:
        return "Error: No List Specified"
    if 'uid' not in request.args:
        return "Error: No User Specified"
    if 'count' not in request.args:
        return "Error: No Count Specified"
    uid = request.args['uid']
    nolist = request.args['list']
    count = int(request.args['count'])
    cursor = db.connection.cursor()
    # NOTE: Get a whole wheel's worth just in case, but only return the top $count
    query = 'SELECT songlists.slid, artists.artist, titles.title, songlists.plays, songlists.uid '
    query += 'FROM songlists INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.aid '
    query += 'WHERE uid = %s AND slid NOT IN (%s) ORDER BY plays ASC, lastplayed ASC LIMIT 50'
    cursor.execute(query, (uid, nolist))
    result = cursor.fetchall()
    random.shuffle(result)
    return jsonify(result[0:count])

# 'sid' is the **SLID** in songlists to update
# TODO: Add some form of auth around this


@app.route('/api/v1/play', methods=['GET'])
def playSong():
    if 'sid' not in request.args:
        return "Error: No Song Specified"
    songid = request.args['sid']
    cursor = db.connection.cursor()
    query = 'UPDATE songlists SET plays = plays + 1, lastplayed = current_date() WHERE slid = %s'
    cursor.execute(query, (songid,))
    result = cursor.fetchall()
    return jsonify(result)

# 'uid' is the userid for the songs to pull
# Sorts by IDK (add as a param?)
# Does not do pagination


@app.route('/api/v1/getpubsongs', methods=['GET'])
def getPublicList():
    if 'uid' not in request.args:
        return "Error: No user specified"
    # TODO: Add pagination?
    uid = request.args['uid']
    cursor = db.connection.cursor()
    query = 'SELECT songlists.slid, artists.artist, titles.title, songlists.plays, songlists.lastplayed '
    query += 'FROM songlists INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON songs.aid = artists.aid '
    query += 'INNER JOIN titles ON songs.tid = titles.tid '
    query += 'WHERE uid = %s AND public = 1'
    cursor.execute(query, (uid,))
    result = cursor.fetchall()
    return jsonify(result)

# getRequests: Get the list of outstanding requests for a user
# uid: the user to get requests for
# limit: the max number of requests to get/clear TODO
# TODO: This MUST have authentication since it eats requests!!!!!!!!!!!


@app.route('/api/v1/getreqs', methods=['GET'])
def getRequests():
    if 'uid' not in request.args:
        return "Error: No User Specified"
    uid = int(request.args['uid'])
    limit = 0
    if 'limit' in request.args:
        limit = int(request.args['limit'])
    cursor = db.connection.cursor()
    query = 'SELECT requests.rid, requests.slid, users.username, artists.artist, titles.title, requests.prio '
    query += 'FROM requests INNER JOIN songlists ON requests.uid = songlists.uid '
    query += 'AND requests.slid = songlists.slid INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid '
    query += 'INNER JOIN artists ON artists.aid = songs.tid '
    query += 'LEFT JOIN users ON requests.ruid = users.uid '
    query += 'WHERE requests.uid = %s ORDER BY requests.timestamp ASC'
    cursor.execute(query, (uid,))
    result = cursor.fetchall()
    return jsonify(result)

# addRequest: Adds a request for a specific user
# uid: User to create the request for
# slid: Specific songlist entry to request


@app.route('/api/v1/addreq', methods=['GET'])
def addRequest():
    ruid = 0
    if g.uid is not None:
        ruid = g.uid
    if 'slid' not in request.args:
        return "Error: No Song Specified"
    slid = int(request.args['slid'])
    cursor = db.connection.cursor()
    query = 'INSERT INTO requests (uid, ruid, slid, timestamp) '
    query += 'SELECT uid, %s, slid, NOW() FROM songlists '
    query += 'WHERE slid = %s'

    cursor.execute(query, (ruid, slid,))
    db.connection.commit()
    result = cursor.fetchall()
    return jsonify(result)

# removereq - Removes a request from the overall request message queue
# rid - the key for the request to knock out of the message queue


@app.route('/api/v1/removereq', methods=['GET'])
def removeRequest():
    if 'rid' not in request.args:
        return "No dice"
    rid = int(request.args['rid'])
    cursor = db.connection.cursor()
    query = 'DELETE FROM requests WHERE rid = %s'
    cursor.execute(query, (rid,))
    db.connection.commit()
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/addsong', methods=['POST'])
def addSong():
    songtitle = request.json['title']
    songartist = request.json['artist']
    public = int(request.json['pub'])
    uid = int(request.json['uid'])
    link = request.json['link']
    sid = findOrAddSong(songartist, songtitle, link)
    cursor = db.connection.cursor()
    query = 'INSERT INTO songlists (uid, sid, public) VALUES (%s, %s, %s)'
    cursor.execute(query, (uid, sid, public,))
    db.connection.commit()
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/delsong', methods=['POST'])
def removeSongFromList():
    slid = int(request.json['slid'])
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM songlists WHERE slid = %s'
    cursor.execute(query, (slid,))
    result = cursor.fetchone()
    # You can only edit your own songlist
    if (result['uid'] != session['uid']):
        return 'Invalid User', 401
    query = 'DELETE FROM songlists WHERE slid = %s'
    cursor.execute(query, (slid,))
    result = cursor.fetchone()
    return 'OK'

####################
# Helper functions #
####################


def addNewUser(username, password, email, uid=-1, tuid=''):
    cursor = db.connection.cursor()
    if uid == -1:
        # Create a Username/Password user
        query = 'INSERT INTO users (username, password, email) VALUES (%s, %s, %s)'
        cursor.execute(query, (username, password, email,))
        result = cursor.fetchall()
    else:
        # Create a Twitch-based user
        query = 'INSERT INTO users (uid, username, password, email, twitch) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(query, (uid, username, password, email, tuid,))
        result = cursor.fetchall()
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    return int(row['uid'])


def getVideoId(link):
    query = urlparse.urlparse(link)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urlparse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    return ''


def findOrAddSong(artist, title, link):
    aid = -1
    tid = -1
    cursor = db.connection.cursor()
    # Artist ID
    query = 'SELECT aid FROM artists WHERE artist = %s'
    cursor.execute(query, (artist,))
    result = cursor.fetchall()
    if (len(result) == 0):  # Artist Doesn't exist
        query = 'INSERT INTO artists (artist) VALUES (%s)'
        cursor.execute(query, (artist,))
        db.connection.commit()
        query = 'SELECT aid FROM artists WHERE artist = %s'
        cursor.execute(query, (artist,))
        result = cursor.fetchall()
    aid = int(result[0]['aid'])
    # Title ID
    query = 'SELECT tid FROM titles WHERE title = %s'
    cursor.execute(query, (title,))
    result = cursor.fetchall()
    if (len(result) == 0):  # Title Doesn't exist
        query = 'INSERT INTO titles (title) VALUES (%s)'
        db.connection.commit()
        cursor.execute(query, (title,))
        query = 'SELECT tid FROM titles WHERE title = %s'
        cursor.execute(query, (title,))
        result = cursor.fetchall()
    tid = int(result[0]['tid'])
    # Actual Song ID
    query = 'SELECT sid FROM songs WHERE artist = %s AND title = %s'
    cursor.execute(query, (aid, tid,))
    result = cursor.fetchall()
    if (len(result) == 0):  # SONG doesn't exist
        ytid = getVideoId(link)
        query = 'INSERT INTO songs (artist, title, ytid) VALUES (%s, %s, %s)'
        cursor.execute(query, (aid, tid, ytid))
        db.connection.commit()
        query = 'SELECT sid FROM songs WHERE artist = %s AND title = %s'
        cursor.execute(query, (aid, tid,))
        result = cursor.fetchall()
    return result[0]['sid']


if __name__ == '__main__':
    app.run()
