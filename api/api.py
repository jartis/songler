import flask
import mysql.connector
import random
from flask import request, jsonify
from dbconf import *

app = flask.Flask(
    __name__,
    static_url_path='',
    static_folder='../frontend')
app.config["DEBUG"] = True

songlerdb = mysql.connector.connect(
    host=dbhost,
    user=dbuser,
    password=dbpass,
    port=dbport,
    database="songler"
)

# 'uid' is the user to get the song(list) for
# Sorts on plays/lastplayed by default


@app.route('/api/v1/songlist', methods=['GET'])
def getAllUserSongs():
    if 'uid' not in request.args:
        return "Error: No User Specified"
    cursor = songlerdb.cursor(dictionary=True)
    query =  'SELECT songlists.slid, artists.artist, titles.title, songlists.public, songlists.plays, '
    query += 'songlists.userid, songlists.lastplayed FROM songlists '
    query += 'INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON artists.aid = songs.artist '
    query += 'INNER JOIN titles ON titles.tid = songs.title '
    query += 'WHERE userid = %s ORDER BY plays ASC, lastplayed ASC'
    cursor.execute(query, (request.args['uid'],))
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
    count = request.args['count']
    cursor = songlerdb.cursor(dictionary=True)
    query =  'SELECT songlists.slid, artists.artist, titles.title, songlists.plays, songlists.userid '
    query += 'FROM songlists INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON artists.aid = songs.artist '
    query += 'INNER JOIN titles ON titles.tid = songs.title '
    query += 'WHERE userid = %s AND slid NOT IN (%s) ORDER BY plays ASC, lastplayed ASC LIMIT 50'
    formatlist = ','.join(map(str, nolist))
    cursor.execute(query, (uid, nolist))
    result = cursor.fetchall()
    random.shuffle(result)
    return jsonify(result[0:10])

# 'sid' is the **SLID** in songlists to update
# TODO: Add some form of auth around this


@app.route('/api/v1/play', methods=['GET'])
def playSong():
    if 'sid' not in request.args:
        return "Error: No Song Specified"
    songid = request.args['sid']
    cursor = songlerdb.cursor(dictionary=True)
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
    cursor = songlerdb.cursor(dictionary=True)
    query =  'SELECT songlists.slid, artists.artist, titles.title, songlists.plays, songlists.lastplayed '
    query += 'FROM songlists INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON songs.artist = artists.aid '
    query += 'INNER JOIN titles ON songs.title = titles.tid '
    query += 'WHERE userid = %s AND public = 1'
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
    cursor = songlerdb.cursor(dictionary=True)
    query =  'SELECT requests.rid, requests.slid, artists.artist, titles.title, requests.prio '
    query += 'FROM requests INNER JOIN songlists ON requests.uid = songlists.userid '
    query += 'AND requests.slid = songlists.slid INNER JOIN songs on songs.sid = songlists.sid '
    query += 'INNER JOIN titles on songs.title = titles.tid INNER JOIN artists on artists.aid = songs.artist '
    query += 'WHERE requests.uid = %s ORDER BY requests.timestamp ASC'
    cursor.execute(query, (uid,))
    result = cursor.fetchall()
    return jsonify(result)

# addRequest: Adds a request for a specific user
# uid: User to create the request for
# slid: Specific songlist entry to request


@app.route('/api/v1/addreq', methods=['GET'])
def addRequest():
    if 'uid' not in request.args:
        return "Error: No User Specified"
    uid = int(request.args['uid'])
    if 'slid' not in request.args:
        return "Error: No Song Specified"
    slid = int(request.args['slid'])
    cursor = songlerdb.cursor(dictionary=True)
    query = 'INSERT INTO requests (uid, slid, timestamp) VALUES (%s, %s, NOW())'
    cursor.execute(query, (uid, slid,))
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/v1/removereq', methods=['GET'])
def removeRequest():
    if 'rid' not in request.args:
        return "No dice"
    rid = int(request.args['rid'])
    cursor = songlerdb.cursor(dictionary=True)
    query = 'DELETE FROM requests WHERE rid = %s'
    cursor.execute(query, (rid,))
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/api/v1/addsong', methods=['POST'])
def addSong():
    songtitle = request.json['title']
    songartist = request.json['artist']
    public = int(request.json['pub'])
    uid = int(request.json['uid'])
    sid = findSong(songartist, songtitle)
    cursor = songlerdb.cursor(dictionary=True)
    query = 'INSERT INTO songlists (userid, sid, public) VALUES (%s, %s, %s)'
    cursor.execute(query, (uid, sid, public,))
    result = cursor.fetchall()
    return jsonify(result)

def findSong(artist, title):
    aid = -1
    tid = -1
    cursor = songlerdb.cursor()
    # Artist ID
    query = 'SELECT aid FROM artists WHERE artist = %s'
    cursor.execute(query, (artist,))
    result = cursor.fetchall()
    if (len(result) == 0): # Artist Doesn't exist
        query = 'INSERT INTO artists (artist) VALUES (%s)'
        cursor.execute(query, (artist,))
        result = cursor.fetchall()
    aid = result[0]
    # Title ID
    query = 'SELECT tid FROM titles WHERE title = %s'
    cursor.execute(query, (title,))
    result = cursor.fetchall()
    if (len(result) == 0): # Title Doesn't exist
        query = 'INSERT INTO titles (title) VALUES (%s)'
        cursor.execute(query, (title,))
        result = cursor.fetchall()
    tid = result[0]
    # Actual Song ID
    query = 'SELECT sid FROM songs WHERE artist = %s AND title = %s'
    cursor.execute(query, (aid, tid,))
    result = cursor.fetchall()
    if (len(result) == 0): # SONG doesn't exist
        query = 'INSERT INTO songs (artist, title) VALUES (%s, %s)'
        cursor.execute(query, (aid, tid,))
        result = cursor.fetchall()        
    return result[0]

app.run()
