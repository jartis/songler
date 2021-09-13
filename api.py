from app import app, addNewUser, getVideoId
import auth
import routes
import random
from flask import Flask, url_for, redirect, request, jsonify, render_template, g, session, flash
from flask_bcrypt import Bcrypt
from flask_oauthlib.client import OAuth
from enum import IntEnum
from urllib.parse import urlparse
from urllib import parse
from thefuzz import fuzz
from thefuzz import process
from dbutil import *
import random


@app.route('/api/v1/getconfig', methods=['GET', ])
def api_getconfig():
    """
    Pulls a blob of JSON configuration from the DB for a user.
    Returns JSON, or 'NG' is no configuration is found.
    """
    if (session['uid']) == 0:
        return 'NG'
    result = getOverlayConfig(session['uid'])
    if (result == ''):
        return 'NG'
    return jsonify(result)


@app.route('/api/v1/saveconfig', methods=['POST', ])
def api_saveconfig():
    """
    Stores a blob of config data in the DB from an overlay page.
    """
    if (session['uid']) == 0:
        return 'NG'
    config = request.json['config']
    uid = session['uid']
    result = saveOverlayConfig(uid, config)
    if (result == 0):
        return 'NG'
    return 'OK'


@app.route('/api/v1/checkuser/<username>', methods=['GET', ])
def api_checkuser(username):
    """
    Searches for <user> as a username in the user table.
    Returns 1 or 0.
    """
    return usernameInUse(username)


@app.route('/api/v1/checkemail/<email>', methods=['GET', ])
def api_checkemail(email):
    """
    Searches for <email> in the user table.
    Returns 1 or 0.
    """
    return emailInUse(email)


@app.route('/api/v1/allsongs', methods=['GET'])
@app.route('/api/v1/allsongs/<uid>', methods=['GET'])
def api_allsongs(uid = -1):
    """
    Gets all songs for the currently logged in user.
    Sorts by least played, then least recently played.
    """
    if (uid == -1):
        if (session['uid'] == 0):
            return 'NG'
        uid = int(session['uid'])
    result = getUserSongs(uid, False)
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
    result = getRefillSongs(uid, nolist)
    random.shuffle(result)
    return jsonify(result[0:count])


@app.route('/api/v1/playslid/<slid>', methods=['GET'])
def api_playslid(slid):
    """
    Increments the play count and sets the last played date to now, for a given songlist id.
    <slid>: Songlist ID to update.
    TODO: Add authorization that this is called by the owning user.
    """
    slid = int(slid)
    date = 0
    if 'date' in request.args:
        date = request.args['date']
    count = playSong(slid, date)
    if (count > 0):
        return 'OK'
    return 'NG'


@app.route('/api/v1/playreq/<rid>', methods=['GET'])
def api_playreq(rid):
    """
    Increments the play count and sets the last played date to now, for a given request id.
    <rid>: Request ID to update.
    TODO: Add authorization that this is called by the owning user.
    """
    rid = int(rid)
    slid = getSlidFromRid(rid)
    count = playSong(slid, 0)
    if (count > 0):
        return 'OK'
    return 'NG'


@app.route('/api/v1/getpubsongs/<uid>', methods=['GET'])
def api_getpubsongs(uid):
    """
    Gets the full list of publicly visible songs for a user.
    <uid>: The user whose songlist we are getting.
    """
    uid = int(uid)
    result = getUserSongs(uid, True)
    return jsonify(result)


@app.route('/api/v1/userinfo/<uid>', methods=['GET'])
def api_userinfo(uid):
    """
    Gets the username, Twitch UID, membership date from the user table for a user.
    <uid> - The user to get the info about.
    """
    result = getUserInfo(int(uid))
    return jsonify(result)


@app.route('/api/v1/reqcount', methods=['GET'])
def api_reqcount():
    """
    Gets count of requests for current logged in user.
    """
    uid = g.uid
    if (uid == 0):
        return '0'
    return str(getReqCount(uid))


@app.route('/api/v1/getreqs', methods=['GET'])
def api_getreqs():
    """
    Gets the pending requests for current logged in user.
    TODO: Support actually limiting the number of requests to grab out of the request MQ
    """
    uid = session['uid']
    limit = 0
    if 'limit' in request.args:
        limit = int(request.args['limit'])
    result = getRequests(uid, limit)
    return jsonify(result)


@app.route('/api/v1/addreq/<slid>', methods=['GET'])
def api_addreq(slid):
    """
    Adds a request to the request MQ. Assumes the request source from the session's UID.
    Returns 'QF' if requester has a requests in the target users MQ already - UNLESS you are the song owner.
    <slid> - Songlist ID to request, reads target user ID from songlist.
    """
    ruid = 0
    rname = 'Anonymous'
    if (g.uid is not None):
        ruid = g.uid
        rname = g.displayname
    # TODO: Fix this priority crud
    prio = 0
    if (request.args.get('p') is not None):
        prio = int(request.args.get('p'))
    slid = int(slid)
    # First, a rate limit check - is there a request for target user in the
    # Request MQ from us alread?
    if (canMakeRequest(ruid, slid) is False):
        return 'QF'
    count = addRequest(ruid, rname, prio, slid)
    if (count > 0):
        return 'OK'
    return 'NG'


@app.route('/api/v1/removereq/<rid>', methods=['GET'])
def api_removereq(rid):
    """
    Removes a request from the Request MQ.
    <rid>: Request id to remove.
    """
    count = removeRequest(int(rid), session['uid'])
    if (count > 0):
        return 'OK'
    return 'NG'


@app.route('/api/v1/addsong', methods=['POST'])
def api_addsong():
    """
    Adds a new song to a user's songlist.
    Creates a new artist and title entry if necessary.
    TODO: Use session vars to determine user whose list to add to.
    """
    songtitle = request.json['title']
    songartist = request.json['artist']
    public = int(request.json['pub'])
    wheel = int(request.json['wheel'])
    uid = int(request.json['uid'])
    link = request.json['link']
    sid = findOrAddSong(songartist, songtitle)
    ytid = getVideoId(link)
    count = findSongOnUserSonglist(sid, uid)
    if (count > 0):
        return 'SE'
    count = addSongToSonglist(uid, sid, ytid, public, wheel)
    if (count > 0):
        return 'OK'
    return 'NG'


@app.route('/api/v1/artistinfo/<aid>', methods=['GET'])
def api_artistinfo(aid):
    """
    Gets artist 'profile' info for a specified artist id.
    <aid> - Artist ID to get profile page for.
    """
    aid = int(aid)
    artist = getArtistInfo(aid)
    artist['songs'] = getSongsForArtist(aid)
    artist['users'] = getUsersForArtist(aid)
    return jsonify(artist)


@app.route('/api/v1/setshowreq', methods=['POST'])
def api_setshownames():
    """
    Sets the "Show/Hide requester names" flag on the current logged in user's account.
    POST: show = 0/1 for the flag (1 to show, 0 to hide)
    """
    if (session['uid'] == 0):
        return 'NG'
    show = int(request.json['show'])
    result = setShowNames(uid, show)
    if (result > 0):
        return str(show)
    return 'N'


@app.route('/api/v1/setanon', methods=['POST'])
def api_setanon():
    """
    Sets the "Allow anonymous requests" flag on the current logged in user's account.
    POST: show = 0/1 for the flag (1 to show, 0 to hide)
    """
    if (session['uid'] == 0):
        return 'NG'
    anon = int(request.json['anon'])
    result = setAnon(session['uid'], show)
    if (result > 0):
        return str(anon)
    return 'NG'


@app.route('/api/v1/getshowreq', methods=['GET'])
@app.route('/api/v1/getshowreq/<uid>', methods=['GET'])
def api_getshownames(uid=0):
    """
    Gets the show/hide requester names flag for the current logged in user.
    Defaults to a zero if not logged in or anything like that.
    """
    if (uid == 0):
        if (session['uid'] == 0):
            return 'NG'
        uid = int(session['uid'])
    return getShowNames(uid)


@app.route('/api/v1/getanon', methods=['GET'])
@app.route('/api/v1/getanon/<uid>', methods=['GET'])
def api_getanon(uid=0):
    """
    Gets the allow anonymous requests flag for the current logged in user.
    Defaults to a zero if not logged in or anything like that.
    """
    uid = int(uid)
    if (uid == 0):
        if (session['uid'] == 0):
            return 'NG'
        uid = int(session['uid'])
    return getAnon(uid)


@app.route('/api/v1/setdisplayname', methods=['POST'])
def api_setdisplayname():
    """
    Sets the display name for the currently logged in user.
    """
    if (session['uid'] == 0):
        return 'NG'
    dname = request.json['dname']
    result = setDisplayName(dname, session['uid'])
    if (result < 1):
        return 'NG'
    session['displayname'] = dname
    return 'OK'


@app.route('/api/v1/songinfo/<sid>', methods=['GET'])
def api_songinfo(sid):
    """
    Gets song 'profile' info for a specified song id.
    Returns songinfo: {artist, title, users[{displayname, username}], plays, recent}
    <sid> - Song ID to get profile page for.
    """
    songinfo = getSongArtistTitle(int(sid))
    songinfo['users'] = getPublicSonglistUsersForSid(int(sid))
    songInfo['plays'] = getTotalPlaysForSid(int(sid))
    songInfo['recent'] = getMostRecentPlayForSid(int(sid))
    return jsonify(songinfo)


@app.route('/api/v1/alluserdnames', methods=['GET'])
def api_alluserdnames():
    """
    Get a raw list of user displaynames for populating autocomplete box.
    """
    result = getUserDisplayNames()
    return jsonify(result)


@app.route('/api/v1/allartists', methods=['GET'])
def api_allartists():
    """
    Get a raw list of artists and aids for populating autocomplete box.
    """
    result = getAllArtists()
    return jsonify(result)


@app.route('/api/v1/alltitles', methods=['GET'])
def api_alltitles():
    """
    Get a raw list of titles and tids for populating autocomplete box.
    """
    result = getAllTitles()
    return jsonify(result)


@app.route('/api/v1/delsong', methods=['POST'])
def api_delsong():
    """
    Removes a song from a user's songlist.
    'slid' - Songlist entry to delete.
    Returns 'NG' on an error, 'OK' on a successful delete.
    """
    slid = int(request.json['slid'])
    uid = session['uid']
    count = deleteSlidFromSonglist(slid, uid)
    if (count == 0):
        return 'NG'
    return 'OK'


@app.route('/api/v1/allsonginfos', methods=['GET'])
def api_allsonginfos():
    """
    Returns a list of all songs (artist, title, sid) for populating the autocomplete.
    """
    result = getAllArtistsAndTitlesAndSids()
    return jsonify(result)


@app.route('/api/v1/setsongpub/<slid>/<pub>', methods=['GET'])
def api_setsongpug(slid, pub):
    """
    Sets a songlist entry to public or non-public, if the session GUID matches the songlist entry owner.
    <slid> - Songlist entry to update
    <pub> - 1 or 0 (for True or False)
    Returns OK if a row was updated, NG if no change was made (ie., UID doesn't match).
    """
    count = setSongPub(int(pub), int(slid), session['uid'])
    if (count == 1):
        return 'OK'
    return 'NG'


@app.route('/api/v1/setsongwheel/<slid>/<wheel>', methods=['GET'])
def api_setsongwheel(slid, wheel):
    """
    Sets a songlist entry to "wheel-able" or not, if the session GUID matches the songlist entry owner.
    <slid> - Songlist entry to update
    <wheel> - 1 or 0 (for True or False)
    Returns OK if a row was updated, NG if no change was made (ie., UID doesn't match).
    """
    count = setSongWheel(int(wheel), int(slid), session['uid'])
    if (count == 1):
        return 'OK'
    return 'NG'
