from app import app, db
import api
import auth
import random
from flask import Flask, url_for, redirect, request, jsonify, render_template, g, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
from enum import IntEnum
from urllib.parse import urlparse
from dbconf import *


@app.route('/login')
def renderLogin():
    """
    Shows the login page.
    """
    return render_template('login.jinja')


@app.route('/newuser')
def newuser():
    """
    Shows the Create (native) User page
    """
    return render_template('newuser.jinja')


@app.route('/wheel')
def renderWheel():
    """
    Shows the current logged-in user's overlay page.
    """
    if g.uid is None:
        return render_template('error.jinja', error=("You must be logged in to view your overlay"))
    return render_template('wheel.jinja', uid=g.uid, username=g.username, loggedIn=g.loggedin)


@app.route('/')
@app.route('/home')
def renderHome():
    """
    Shows the homepage.
    """
    return render_template('home.jinja', username=g.username, loggedIn=g.loggedin)


@app.route('/songlist/<user>', methods=['GET', ])
def showSongList(user):
    """
    Shows the public songlist for a given user.
    <user> - The username for the songlist we want to display.
    """
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


@app.route('/managelist', methods=['GET', ])
def manageSongList():
    """
    Shows the song list manager / editor for the current logged in user.
    """
    if int(g.uid) > 0:
        return render_template('managelist.jinja', uid=g.uid, username=g.username, loggedIn=g.loggedin)
    else:
        return render_template('error.jinja', error=("No songlist found for user " + g.username), username=g.username, loggedIn=g.loggedin)


@app.route('/profile/<user>', methods=['GET', ])
def renderProfile(user):
    """
    Gets the profile page for the specified user.
    <user> - Username for the profile page to retrieve.
    """
    user = str(user)
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, [user, ])
    row = cursor.fetchone()
    if row is not None:
        uid = int(row['uid'])
        return render_template('profile.jinja', uid=g.uid, listuid=uid, listuser=user, username=g.username, loggedIn=g.loggedin)
    else:
        return render_template('error.jinja', error=("No user found with the name " + user), username=g.username, loggedIn=g.loggedin)


@app.route('/song/<sid>', methods=['GET', ])
def songInfo(sid):
    """
    Gets a song's "Profile Page".
    <sid> - Song ID for the relevant song.
    """
    sid = int(sid)
    return render_template('song.jinja', uid=g.uid, username=g.username, loggedIn=g.loggedin, sid=sid)
