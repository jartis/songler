from flask import Blueprint
from dbutil import *

nb_blueprint = Blueprint('nb_blueprint', __name__)


@nb_blueprint.route('/api/v1/nbrand', methods=['GET'])
def nbrand():
    """
    Adds a random song request from the user (via Nightbot).
    """
    userString = request.headers.get('Nightbot-User', None)
    channelString = request.headers.get('Nightbot-Channel', None)
    if (channelString is None or userString is None):
        return 'This endpoint can only be called by Nightbot.'
    # Who is the request FOR?
    channelInfo = dict(parse.parse_qsl(channelString))
    channelName = channelInfo.get('displayName')
    # Who is the request FROM?
    userInfo = dict(parse.parse_qsl(userString))
    reqUsername = userInfo.get('displayName')
    reqUID = userInfo.get('providerId')
    # Sigh... get the UID from the twitch name for the channel...
    channelUID = getUidFromTName(channelName)
    if (ChannelUID == -1):
        return 'There was an error requesting your random song!'
    # Then get all the public songs for the user...
    results = getUserSongs(channelUID, True)
    # Now pick one at random...
    random.shuffle(results)
    song = results[0]
    slid = song['slid']
    sn = song['title'] + ' by ' + song['artist']
    # FINALLY put in the actual request
    canRequest = canMakeRequest(reqUID, slid)
    if (canRequest == 'K'):
        addRequest(reqUID, reqUsername, 0, slid)
        return f'{reqUsername}, your request for {sn} has been added to the queue!'
    elif (canRequest == 'U'):
        return f'{reqUsername}, you already have a request in the queue.'
    elif (canRequest == 'S'):
        return f'{reqUsername}, this song is already in the request queue.'
    # And a failsafe
    return f'{reqUsername}, there was an error requesting this song.'


@nb_blueprint.route('/api/v1/nbreq', methods=['GET'])
def nbreq():
    """
    Finds the closest match for a given search string and adds a request if able.
    Takes get parameter(s) for a song title or artist+title.
    If the request comes from Nightbot, we get some headers for free!
    Nightbot-User: name=night&displayName=night&provider=twitch&providerId=11785491&userLevel=owner
    Nightbot-Channel: name=night&displayName=Night&provider=twitch&providerId=11785491
    """
    userString = request.headers.get('Nightbot-User', None)
    channelString = request.headers.get('Nightbot-Channel', None)
    searchString = request.args.get('s', None)
    if (channelString is None or userString is None or searchString is None):
        return 'This endpoint can only be called by Nightbot.'
    searchString = searchString.lower()
    # Who is the request FOR?
    channelInfo = dict(parse.parse_qsl(channelString))
    channelName = channelInfo.get('displayName')
    # Who is the request FROM?
    userInfo = dict(parse.parse_qsl(userString))
    reqUsername = userInfo.get('displayName')
    reqUID = userInfo.get('providerId')
    # Sigh... get the UID from the twitch name for the channel...
    channelUID = getUidFromTName(channelName)
    if (ChannelUID == -1):
        return 'There was an error requesting your song!'
    # Then get all the public songs for the user...
    results = getUserSongs(channelUID, True)
    songstrings = [r['artist'].lower() + ' ' + r['title'].lower()
                   for r in results]
    match = process.extractOne(searchString, songstrings)
    if (match[1] < 90):  # Arbitrary limit for closest match
        return 'No match found for your request.'
    # Okay, get the ACTUAL song from that perfect match
    song = next((s for s in results if (
        s['artist'].lower() + ' ' + s['title'].lower()) == match[0]), None)
    if (song is None):
        return 'No match found for your request.'
    slid = song['slid']
    sn = song['title'] + ' by ' + song['artist']
    # FINALLY put in the actual request
    canRequest = canMakeRequest(reqUID, slid)
    if (canRequest == 'K'):
        addRequest(reqUID, reqUsername, 0, slid)
        return f'{reqUsername}, your request for {sn} has been added to the queue!'
    elif (canRequest == 'U'):
        return f'{reqUsername}, you already have a request in the queue.'
    elif (canRequest == 'S'):
        return f'{reqUsername}, this song is already in the request queue.'
    # And a failsafe
    return f'{reqUsername}, there was an error requesting this song.'


@nb_blueprint.route('/api/v1/nbws', methods=['GET'])
def nbws():
    """
    Withdraws (removes) the calling user's last request.
    """
    userString = request.headers.get('Nightbot-User', None)
    channelString = request.headers.get('Nightbot-Channel', None)
    if (channelString is None or userString is None):
        return 'This endpoint can only be called by Nightbot.'
    # Who is the withdraw request FOR?
    channelInfo = dict(parse.parse_qsl(channelString))
    channelName = channelInfo.get('displayName')
    # Who is the withdraw request FROM?
    userInfo = dict(parse.parse_qsl(userString))
    reqUsername = userInfo.get('displayName')
    reqUID = userInfo.get('providerId')
    # Sigh... get the UID from the twitch name for the channel...
    channelUID = getUidFromTName(channelName)
    if (ChannelUID == -1):
        return 'There was an error cancelling your request!'
    # Get the latest request from the request user for the channel user
    rid = getLastRequestInChannel(reqUID, channelUID)
    if (rid == -1):
        return 'You have no pending requests.'
    results = removeRequest(rid, reqUID)
    if (results == 0):
        return 'There was an error cancelling your request!'
    return (f'{reqUsername} has withdrawn their last request.')
