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

@app.route('/api/v1/songlist', methods=['GET'])
def getAllSongs():
    if 'uid' not in request.args:
        return "Error: No User Specified"
    cursor = songlerdb.cursor(dictionary=True)
    query = 'SELECT songlists.slid, songs.artist, songs.title, songlists.plays, songlists.userid FROM songlists INNER JOIN songs ON songs.sid = songlists.sid WHERE userid = %s ORDER BY plays ASC, lastplayed ASC'
    cursor.execute(query, (request.args['uid'],))
    result = cursor.fetchall()
    return jsonify(result)

# 'list' is a comma separated list of song ids to exclude
# 'uid' is the userid for the songs to pull
# 'count' is the number of songs to return
# Sorts by last played date, never and oldest first
@app.route('/api/v1/more', methods=['GET'])
def refillSongs():
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
    query = 'SELECT songlists.slid, songs.artist, songs.title, songlists.plays, songlists.userid FROM songlists INNER JOIN songs ON songs.sid = songlists.sid WHERE userid = %s AND slid NOT IN (%s) ORDER BY plays ASC, lastplayed ASC LIMIT 50'
    formatlist = ','.join(map(str, nolist))
    cursor.execute(query, (uid, nolist))
    result = cursor.fetchall()
    random.shuffle(result)
    return jsonify(result[0:10])

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

app.run()