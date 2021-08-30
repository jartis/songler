from app import app, db
import auth
import render
import random
from flask import Flask, url_for, redirect, request, jsonify, render_template, g, session, flash
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from twitch import *
from enum import IntEnum
from urllib.parse import urlparse

@app.route('/api/v1/getconfig', methods=['GET', ])
def getOverlayConfig():
    """
    Pulls a blob of JSON configuration from the DB for a user.
    Returns JSON, or 0 is no configuration is found.
    """
    if (session['uid']) == 0:
        return '0'
    cursor = db.connection.cursor()
    query = 'SELECT * FROM overlays WHERE uid = %s'
    cursor.execute(query, (session['uid'],))
    row = cursor.fetchall()
    if (len(row) > 0):
        return jsonify(row[0])
    return '0'


@app.route('/api/v1/saveconfig', methods=['POST', ])
def saveOverlayConfig():
    """
    Stores a blob of config data in the DB from an overlay page.
    """
    if (session['uid']) == 0:
        return '0'  # TODO: Do this not-grossly
    config = request.json['config']
    uid = session['uid']
    cursor = db.connection.cursor()
    query = 'SELECT * FROM overlays WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchall()
    if len(result) == 0:
        query = 'INSERT INTO overlays (config, uid) VALUES (%s, %s)'
    else:
        query = 'UPDATE overlays SET config = %s WHERE uid = %s'
    cursor.execute(query, (config, uid,))
    db.connection.commit()
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/checkuser/<user>', methods=['GET', ])
def checkuser(user):
    """
    Searches for <user> as a username in the user table.
    Returns 1 or 0.
    """
    user = str(user).replace('%', '\%').replace('_', '\_')
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, (user, ))
    row = cursor.fetchone()
    if row is not None:
        return '1'
    return '0'


@app.route('/api/v1/checkemail/<email>', methods=['GET', ])
def checkemail(email):
    """
    Searches for <email> in the user table.
    Returns 1 or 0.
    """
    email = str(email).replace('%', '\%').replace('_', '\_')
    cursor = db.connection.cursor()
    query = 'SELECT uid FROM users WHERE email LIKE %s'
    cursor.execute(query, [email, ])
    row = cursor.fetchone()
    if row is not None:
        return '1'
    return '0'


@app.route('/api/v1/allsongs/<uid>', methods=['GET'])
def getAllUserSongs(uid):
    """
    Gets all songs for a specified user <uid>. 
    Sorts by least played, then least recently played.
    """
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


@app.route('/api/v1/more', methods=['GET'])
def refillUserSongs():
    """
    Gets a list of songs from a user's songlist. Request must include:
    <list> - a comma separated list of slids to exclude from the search
    <uid> - the uid of the user for the songlist to retrieve
    <count> - maximum number of songs to retrieve
    Sorts by last played date, 'never' then oldest.
    """
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


@app.route('/api/v1/play', methods=['GET'])
def playSong():
    """
    Increments the play count and sets the last played date to now, for a given songlist id.
    'sid': Songlist ID to update.
    TODO: Add authorization that this is called by the owning user.
    """
    if 'sid' not in request.args:
        return "Error: No Song Specified"
    songid = request.args['sid']
    cursor = db.connection.cursor()
    query = 'UPDATE songlists SET plays = plays + 1, lastplayed = current_date() WHERE slid = %s'
    cursor.execute(query, (songid,))
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/getpubsongs', methods=['GET'])
def getPublicList():
    """
    Gets the full list of publicly visible songs for a user.
    'uid': The user whose songlist we are getting.
    TODO: Does not natively do any pagination.
    TODO: Does not sort by default.
    """
    if 'uid' not in request.args:
        return "Error: No user specified"
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


@app.route('/api/v1/userinfo/<uid>', methods=['GET'])
def getUserInfo(uid):
    """
    Gets the username, Twitch UID, membership date from the user table for a user.
    <uid> - The user to get the info about.
    """
    cursor = db.connection.cursor()
    query = 'SELECT username, twitch, signup FROM users WHERE uid = %s'
    cursor.execute(query, (int(uid),))
    result = cursor.fetchone()
    return jsonify(result)


@app.route('/api/v1/getreqs', methods=['GET'])
def getRequests():
    """
    Gets the pending requests for a user.
    'uid' - The user whose requests we are returning.
    TODO: Support actually limiting the number of requests to grab out of the request MQ
    TODO: Make sure we verify authentication since this eats requests!
    """
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
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'LEFT JOIN users ON requests.ruid = users.uid '
    query += 'WHERE requests.uid = %s ORDER BY requests.timestamp ASC'
    cursor.execute(query, (uid,))
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/addreq', methods=['GET'])
def addRequest():
    """
    Adds a request to the request MQ. Assumes the request source from the session's UID.
    'slid' - Songlist ID to request, reads target user ID from songlist.
    """
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


@app.route('/api/v1/removereq', methods=['GET'])
def removeRequest():
    """
    Removes a request from the Request MQ.
    'rid': Request id to remove.
    TODO: Authorize? Requests can only be removed by originator or song owner.
    """
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
    """
    Adds a new song to a user's songlist.
    Creates a new artist and title entry if necessary.
    TODO: Use session vars to determine user whose list to add to.
    """
    songtitle = request.json['title']
    songartist = request.json['artist']
    public = int(request.json['pub'])
    uid = int(request.json['uid'])
    link = request.json['link']
    sid = findOrAddSong(songartist, songtitle, link)
    cursor = db.connection.cursor()
    ytid = getVideoId(link)
    query = 'INSERT INTO songlists (uid, sid, public, ytid) VALUES (%s, %s, %s, %s)'
    cursor.execute(query, (uid, sid, public, ytid,))
    db.connection.commit()
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/songinfo/<sid>', methods=['GET'])
def getSongInfo(sid):
    """
    Gets song 'profile' info for a specified songid.
    <sid> - Song ID to get profile page for.
    """
    song = ''
    query = 'SELECT artists.artist, titles.title FROM songs '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid '
    query += 'WHERE songs.sid = %s'
    cursor = db.connection.cursor()
    cursor.execute(query, (int(sid),))
    result = cursor.fetchone()
    # TODO: Handle a 'None' case gracefully
    # NEXT, we should get a list of users that have this song on their list?
    query = 'SELECT DISTINCT username FROM users '
    query += 'INNER JOIN songlists ON songlists.uid = users.uid '
    query += 'WHERE songlists.sid = %s AND songlists.public = 1'
    cursor.execute(query, (int(sid),))
    result['users'] = cursor.fetchall()
    # How about a total count of plays?
    query = 'SELECT SUM(plays) AS totalplays FROM songlists '
    query += 'WHERE sid = %s'
    cursor.execute(query, (int(sid),))
    result['plays'] = int(cursor.fetchone()['totalplays'])
    # and a most recent play?
    return jsonify(result)


@app.route('/api/v1/users', methods=['GET'])
def getUsers():
    """
    Get a raw list of usernames and uids for populating autocomplete box.
    """
    query = 'SELECT username, uid FROM users'
    cursor = db.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/delsong', methods=['POST'])
def removeSongFromList():
    """
    Removes a song from a user's songlist.
    'slid' - Songlist entry to delete.
    TODO: Verify request is coming from owner of the list.
    """
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


@app.route('/api/v1/allsongs', methods=['GET'])
def getAllSongs():
    """
    Returns a list of all songs (artist, title, sid) for populating the autocomplete.
    """
    query = 'SELECT artists.artist, titles.title, songs.sid FROM songs '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid'
    cursor = db.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return jsonify(result)
