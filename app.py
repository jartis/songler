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


def addNewUser(username, password, email, displayname, uid=-1, tuid=''):
    """
    Adds a new user entry to the database.
    <username>: Desired username for new account.
    <password>: Password for new account. Blank if created with an OAuth provider.
    <email>: Email account to attach to new user. Populated from OAuth provider if possible.
    <uid>: Defaults to -1. If provided, sets UID in DB, if -1, use the Auto-Increment.
    <tuid>: Twitch UID, if account was created with Twitch OAuth.
    """
    cursor = db.connection.cursor()
    if tuid == '':
        # Create a Username/Password user
        query = 'INSERT INTO users (username, password, email, signup, displayname) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password, email, displayname))
    else:
        # Create a Twitch-based user
        query = 'INSERT INTO users (username, password, email, tuid, signup, displayname) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password, email, tuid, username))
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    return int(row['uid'])


def getVideoId(link):
    """
    Takes a youtube link and returns the trimmed video ID.
    <link>: The youtube link to parse.
    """
    if (link == ''):
        return ''
    query = urlparse(link)
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

def getReqCount(uid):
    """
    Get count of requests for a user
    """
    cursor = db.connection.cursor()
    query =  'SELECT COUNT(*) as count FROM requests '
    query += 'WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()['count']
    return result

def findOrAddSong(artist, title):
    """
    Returns a SID for a song, with appropriate artist and title AID and TID values, created new if necessary.
    <artist>: Name of the artist to find or create the AID for.
    <title>: Title of the song to find or create the TID for.
    """
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
    query = 'SELECT sid FROM songs WHERE aid = %s AND tid = %s'
    cursor.execute(query, (aid, tid,))
    result = cursor.fetchall()
    if (len(result) == 0):  # SONG doesn't exist
        query = 'INSERT INTO songs (aid, tid) VALUES (%s, %s)'
        cursor.execute(query, (aid, tid))
        db.connection.commit()
        query = 'SELECT sid FROM songs WHERE aid = %s AND tid = %s'
        cursor.execute(query, (aid, tid,))
        result = cursor.fetchall()
    return result[0]['sid']

import auth
import routes
import api

if __name__ == '__main__':
    app.run(host='0.0.0.0')
