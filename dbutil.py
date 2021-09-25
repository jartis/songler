from conf import *
import mysql.connector as mysql


def getConnection():
    try:
        cnx = mysql.connect(host=dbhost, port=dbport, user=dbuser,
                            password=dbpass, database=dbname)
    except connector.Error as err:
        if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DV_ERROR:
            print("Database does not exist")
        else:
            print(err)
    # the else will happen if there was no error!
    else:
        return cnx
    return cnx


def addNewUser(username, password, email, displayname, uid=-1, tuid='', tname='', sluid='', slname=''):
    """
    Adds a new user entry to the database.
    <username>: Desired username for new account.
    <password>: Password for new account. Blank if created with an OAuth provider.
    <email>: Email account to attach to new user. Populated from OAuth provider if possible.
    <uid>: Defaults to -1. If provided, sets UID in DB, if -1, use the Auto-Increment.
    <tuid>: Twitch UID, if account was created with Twitch OAuth.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    if tuid != '':
        # Create a Twitch-based user
        query = 'INSERT INTO users (username, password, email, tuid, tname, signup, displayname) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password,
                       email, tuid, tname, username))
    elif sluid != '':
        query = 'INSERT INTO users (username, password, email, sluid, slname, signup, displayname) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password,
                       email, sluid, slname, username))
    else:
        # Create a Username/Password user
        query = 'INSERT INTO users (username, password, email, signup, displayname) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)'
        cursor.execute(query, (username, password, email, displayname))
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, (username,))
    row = cursor.fetchone()
    return int(row['uid'])


def setSongWheel(wheel, slid, uid):
    """
    Sets the 'wheel' column to true or false for the given songlist ID.
    <wheel> - True or False for the 'show on wheel' value
    <slid> - Songlist ID 
    <uid> - UID making the change. If this doesn't match the SLID owner, don't change. 
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE songlists SET wheel = %s WHERE slid = %s AND uid = %s'
    cursor.execute(query, (wheel, slid, uid,))
    return cursor.rowcount


def setSongPub(pub, slid, uid):
    """
    Sets the 'public' column to true or false for the given songlist ID.
    <pub> - True or False for the 'show on public list' value
    <slid> - Songlist ID 
    <uid> - UID making the change. If this doesn't match the SLID owner, don't change. 
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE songlists SET public = %s WHERE slid = %s AND uid = %s'
    cursor.execute(query, (pub, slid, uid,))
    return cursor.rowcount


def getAllArtistsAndTitlesAndSids():
    """
    Gets a JSON array of all {artist, title, sid} in songs.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT artists.artist, titles.title, songs.sid FROM songs '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid'
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def deleteSlidFromSonglist(slid, uid):
    """
    Deletes a row from songlists matching the slid and uid provided
    <slid> - The songlist ID to remove (if the UID matches)
    <uid> - The user ID making the request. You can only remove your own songs.
    Returns number of affected rows - 0 for no match, 1 for success.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'DELETE FROM songlists WHERE slid = %s AND uid = %s'
    cursor.execute(query, (slid, uid,))
    return cursor.rowcount


def getAllTitles():
    """
    Get a raw list of titles and tids for populating autocomplete box.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT title, tid FROM titles'
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getAllArtists():
    """
    Get a raw list of artists and aids for populating autocomplete box.
    """
    query = 'SELECT artist, aid FROM artists'
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getUserDisplayNames():
    """
    Get a raw list of user displaynames for populating autocomplete box.
    """
    query = 'SELECT displayname FROM users'
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getSongArtistTitle(sid):
    """
    Gets an {artist, title} from the songlist given a sid
        # TODO: Handle a 'None' case gracefully

    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT artists.artist, titles.title FROM songs '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid '
    query += 'WHERE songs.sid = %s'
    cursor.execute(query, (sid,))
    result = cursor.fetchone()
    return result


def getPublicSonglistUsersForSid(sid):
    """
    Returns a list of {username, displayname} that have the specified sid marked
    public on their songlist.
    <sid> - The sid to find across songlists
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT DISTINCT username, displayname FROM users '
    query += 'INNER JOIN songlists ON songlists.uid = users.uid '
    query += 'WHERE songlists.sid = %s AND songlists.public = 1'
    cursor.execute(query, (sid,))
    result = cursor.fetchall()
    return result


def getTotalPlaysForSid(sid):
    """
    Gets a count of the total plays for a specified sid.
    Returns just the count as an int.
    <sid> - The sid we want a play count for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT COUNT(*) AS totalplays FROM plays '
    query += 'WHERE sid = %s'
    cursor.execute(query, (int(sid),))
    result = int(cursor.fetchone()['totalplays'])
    return result


def getMostRecentPlayForSid(sid):
    """
    Gets the most recent play (timestamp) for a specified sid.
    Returns just the timestamp as an int.
    <sid> - The sid we want the most recent play for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT timestamp FROM plays '
    query += 'WHERE sid = %s ORDER BY timestamp DESC'
    cursor.execute(query, (int(sid),))
    row = cursor.fetchone()
    if (row is None):
        return None
    return row['timestamp']


def setDisplayName(dname, uid):
    """
    Sets the display name for the specified user.
    <dname> - New displayname for specified user
    <uid> - UID to update the displayname
    Returns number of rows updated - 0 for no matching UID / error
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE users SET displayname = %s where uid = %s'
    cursor.execute(query, (dname, uid,))
    return cursor.rowcount


def getOnline(uid):
    """
    Returns the online status of a user, for... nefarious purposes.
    <uid> - User to get the online status for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT online FROM userconf WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    return str(result['online'])


def setOnline(uid, online):
    """
    Set's a user's online/offline (streaming / not streaming or live/not) status
    <uid> - User to update live status for
    <online> - Current "online" status
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE userconf SET online = %s WHERE uid = %s'
    cursor.execute(query, (online, uid,))
    return cursor.rowcount


def getAllowOffline(uid):
    """
    Returns the "Allow Offline Requests" option for a user
    <uid> - User to get the allow-offline option for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT allowoffline FROM userconf WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    return str(result['allowoffline'])


def setAllowOffline(uid, allowoffline):
    """
    Set's a user's "Allow Offline Requests" option
    <uid> - User to update "Allow Offline Requests" option for
    <allowoffline> - Current "allowoffline" status
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE userconf SET allowoffline = %s WHERE uid = %s'
    cursor.execute(query, (allowoffline, uid,))
    return cursor.rowcount


def getAnon(uid):
    """
    Returns the "Allow anonymous requests" config value for the specified user.
    <uid> - User to get the Anon flag for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT allowanon FROM userconf WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    return str(result['allowanon'])


def setAnon(uid, anon):
    """
    Sets the "Allow Anonymous Requests" config value for the specified user.
    <uid> - User to set the Anon flag for
    <anon> - Value to set the Anon flag
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE userconf SET allowanon = %s WHERE uid = %s'
    cursor.execute(query, (anon, uid,))
    return cursor.rowcount


def getShowNames(uid):
    """
    Returns the "Show Requester Names" config value for the specified user.
    <uid> - User to get the ShowNames flag for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT showreqname FROM userconf WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    return str(result['showreqname'])


def setShowNames(uid, show):
    """
    Sets the "Show Requester Names" config value for the specified user.
    <uid> - User to set the ShowNames flag for
    <show> - Value to set the ShowNames flag
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE userconf SET showreqname = %s WHERE uid = %s'
    cursor.execute(query, (show, uid,))
    return cursor.rowcount


def getArtistInfo(aid):
    """
    Gets {artist} name for a specific aid.
    <aid> - Artist ID to get the name for.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT artist FROM artists '
    query += 'WHERE artists.aid = %s'
    cursor.execute(query, (aid,))
    result = cursor.fetchone()
    return result


def getSongsForArtist(aid):
    """
    Gets a list of all songs attached to a specific aid
    <aid> - Artist ID to get the songs for
    Returns a list of {title, sid}
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT titles.title, songs.sid FROM songs '
    query += 'INNER JOIN titles ON songs.tid = titles.tid '
    query += 'WHERE songs.aid = %s'
    cursor.execute(query, (aid,))
    results = cursor.fetchall()
    return results


def getUsersForArtist(aid):
    """
    Gets a list of users that have songs by the specified artist on their (public) songlist.
    <aid> - Artist to match across songlists.
    Returns a list of {displayname}s
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT DISTINCT displayname FROM users '
    query += 'INNER JOIN songlists ON songlists.uid = users.uid '
    query += 'INNER JOIN songs ON songlists.sid = songs.sid '
    query += 'WHERE songs.aid = %s AND songlists.public = TRUE'
    cursor.execute(query, (aid,))
    results = cursor.fetchall()
    return results


def findOrAddSong(artist, title):
    """
    Returns a SID for a song, with appropriate artist and title AID and TID values, created new if necessary.
    <artist>: Name of the artist to find or create the AID for.
    <title>: Title of the song to find or create the TID for.
    """
    aid = -1
    tid = -1
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
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


def findSongOnUserSonglist(sid, uid):
    """
    Finds any entries for a song already existing on a user's songlist.
    <sid> - Song ID to find on the list
    <uid> - User ID for the list to search
    Returns the count of entries matching the sid on the user's list.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT COUNT(*) as count FROM songlists WHERE uid = %s AND sid = %s'
    cursor.execute(query, (uid, sid,))
    result = cursor.fetchone()['count']
    return result


def addSongToSonglist(uid, sid, ytid, pub, wheel):
    """
    Adds a specific song (sid) to a user's songlist with the given config options
    <uid> - User ID of the songlist to modify
    <sid> - Song ID to add to the user's list
    <ytid> - a string with the YouTube UUID for a matching video
    <pub> - Whether the song is marked 'public' or not
    <wheel> - Whether the song is marked 'random-wheel-able' or not
    Returns count of modified rows - 1 if it was inserted, 0 if something went wrong
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'INSERT INTO songlists (uid, sid, public, ytid, wheel) VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(query, (uid, sid, pub, ytid, wheel))
    return cursor.rowcount


def removeRequest(rid, uid):
    """
    Removes a row from the request MQ for the specified rid.
    <rid> - Request ID to knock out
    <uid> - The CALLING USER's userid.
    Note: You can only delete a request FOR, or FROM, the specified UID.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'DELETE FROM requests WHERE rid = %s '
    query += 'AND (ruid = %s OR uid = %s)'
    cursor.execute(query, (rid, uid, uid,))
    return cursor.rowcount


def canMakeRequest(ruid, slid):
    """
    Determines if a user can make a request (ie., doesn't have a pending request in the user's queue)
    <ruid> - Requesting user's UID
    <slid> - Songlist ID being requested
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    # Get the UID, we're gonna need it any old way
    query = 'SELECT uid FROM songlists WHERE slid = %s'
    cursor.execute(query, (slid,))
    result = cursor.fetchone()
    uid = result['uid']
    if (ruid > 0):
        query = 'SELECT rid, uid FROM requests WHERE ruid = %s AND uid = %s'
        cursor.execute(query, (ruid, uid,))
        result = cursor.fetchall()
        if (len(result) > 0):
            if int(uid) != int(ruid):
                # Only bail out if the song owner isn't the one requesting. You can fill your own queue.
                return 'U'  # 'U'ser has a request in the queue already
    query = 'SELECT rid FROM requests WHERE slid = %s AND uid IN '
    query += '(SELECT uid FROM songlists WHERE slid = %s)'
    cursor.execute(query, (slid, slid,))
    result = cursor.fetchall()
    if (len(result) > 0):
        return 'S'  # 'S'ong in queue already
    query = 'SELECT allowoffline, online FROM userconf '
    query += 'WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    if (result['online'] == 0 and result['allowoffline'] == 0):
        if int(uid) != int(ruid):
            return 'O' # User is 'O'ffline and offline requests are disabled
    return 'K'


def addRequest(ruid, rname, prio, slid):
    """
    Adds a request object to the MQ
    <ruid> - Requesting user's UID
    <rname> - Requesting user's displayname
    <prio> - Priority to set for the request
    <slid> - Songlist ID to add a request for
    Returns count of added rows - 0 for no matches, 1 for success
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    if (rname is None):
        rname = 'Anonymous'
    query = 'INSERT INTO requests (uid, ruid, slid, timestamp, rname, prio) '
    query += 'SELECT uid, %s, slid, NOW(), %s, %s FROM songlists '
    query += 'WHERE slid = %s'
    cursor.execute(query, (ruid, rname, prio, slid))
    return cursor.rowcount


def getRequests(uid, limit):
    """
    Gets all the current requests for the specified user
    <uid> - User to grab requests for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT requests.rid, requests.slid, requests.rname, artists.artist, titles.title, '
    query += 'requests.prio, requests.timestamp FROM requests '
    query += 'INNER JOIN songlists ON requests.uid = songlists.uid '
    query += 'AND requests.slid = songlists.slid INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'WHERE requests.uid = %s ORDER BY requests.prio DESC, requests.timestamp ASC'
    if (limit > 0):
        query += ' LIMIT %s'
        cursor.execute(query, (uid, limit,))
    else:
        cursor.execute(query, (uid,))
    result = cursor.fetchall()
    return result


def getReqCount(uid):
    """
    Get count of requests for the specified user.
    <uid> - User to get the current request count for.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT COUNT(*) as count FROM requests '
    query += 'WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()['count']
    return result


def getUserInfo(uid):
    """
    Returns the {uid, username, signup, displayname, tuid, 
    tname, sluid, slname, anon, } info for the specified user.
    <uid> - The user ID to pull the userinfo for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT users.uid, username, signup, displayname, tuid, tname, sluid, slname, '
    query += 'userconf.allowanon, userconf.showreqname, userconf.online, userconf.allowoffline '
    query += 'FROM users '
    query += 'INNER JOIN userconf ON userconf.uid = users.uid '
    query += 'WHERE users.uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    return result


def getUserSongs(uid, pub):
    """
    Returns a list of the songlist entries {slid, artist, title, public, plays,
    lastplayed, uid, wheel} for a specified user's songlist
    <uid> - The user ID to match for the songlist
    <pub> - True or False for "Only get public visible songs"
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT songlists.slid, artists.artist, titles.title, songlists.public, '
    query += 'songlists.uid, songlists.wheel, COUNT(plays.pid) as plays, '
    query += 'MAX(plays.timestamp) as lastplayed FROM songlists '
    query += 'INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.tid '
    query += 'LEFT JOIN plays ON songlists.slid = plays.slid '
    query += 'WHERE uid = %s '
    if (pub):
        query += 'AND songlists.public = 1 '
    query += 'GROUP BY songlists.slid '
    query += 'ORDER BY plays ASC, lastplayed ASC '
    cursor.execute(query, (uid,))
    result = cursor.fetchall()
    return result


def getSlidFromRid(rid):
    """
    Helper function to get a songlist id from a request
    <rid> - Request to pull the SLID from
    """
    rid = int(rid)
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT slid FROM requests WHERE requests.rid = %s'
    cursor.execute(query, (rid,))
    result = cursor.fetchone()
    return int(result['slid'])


def playSong(slid, date=''):
    """
    Add a "play" for a songlist ID
    <slid> - Songlist entry to update
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'INSERT INTO plays (slid, timestamp, sid) '
    query += 'VALUES (%s, '
    if (date != ''):
        query += '\'' + str(date) + '\', '
    else:
        query += 'current_date(), '
    query += '(SELECT sid FROM songlists WHERE slid = %s))'
    cursor.execute(query, (slid, slid,))
    return cursor.rowcount


def emailInUse(email):
    """
    Returns 1 if the email exists in the user table, 0 if not.
    """
    email = str(email).replace('%', r'\%').replace('_', r'\_')
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT uid FROM users WHERE email LIKE %s'
    cursor.execute(query, [email, ])
    row = cursor.fetchone()
    if row is not None:
        return '1'
    return '0'


def usernameInUser(username):
    """
    Returns 1 if the username exists in the user table, 0 if not.
    """
    user = str(user).replace('%', r'\%').replace('_', r'\_')
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT uid FROM users WHERE username LIKE %s'
    cursor.execute(query, (user, ))
    row = cursor.fetchone()
    if row is not None:
        return '1'
    return '0'


def getOverlayConfig(uid):
    """
    Pulls the overlay configuration for the specified UserID
    <uid> - User to get the config for
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT * FROM overlays WHERE uid = %s'
    cursor.execute(query, (uid,))
    row = cursor.fetchall()
    if (len(row) > 0):
        return row[0]
    return ''


def saveOverlayConfig(uid, config):
    """
    Saves the current wheel configuration for the specified UID
    <uid> - User to save the config for
    <config> - Big ol gross blob of JSON holding a wheel configuration
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT * FROM overlays WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.rowcount
    if result == 0:
        query = 'INSERT INTO overlays (config, uid) VALUES (%s, %s)'
    else:
        query = 'UPDATE overlays SET config = %s WHERE uid = %s'
    cursor.execute(query, (config, uid,))
    return cursor.rowcount


def getRefillSongs(uid, nolist):
    """
    Gets up to 50 songs from a user's songlist to refill (randomly) the wheel or queue
    <uid> - User to pull songlist items from
    <nolist> - A list of SLIDs to exclude
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    # NOTE: Get a whole wheel's worth just in case, but only return the top $count
    query = 'SELECT songlists.slid, artists.artist, titles.title, songlists.uid '
    query += 'FROM songlists INNER JOIN songs ON songs.sid = songlists.sid '
    query += 'INNER JOIN artists ON artists.aid = songs.aid '
    query += 'INNER JOIN titles ON titles.tid = songs.aid '
    query += 'WHERE uid = %s AND slid NOT IN (%s) AND wheel = 1 '
    query += 'LIMIT 50'
    cursor.execute(query, (uid, nolist))
    result = cursor.fetchall()
    return result


def getUidFromTName(tname):
    """
    Gets a UID given a twitch username.
    <tname> - Twitch username to match
    Returns -1 on no match
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT uid FROM users WHERE tname = %s'
    cursor.execute(query, (channelName,))
    results = cursor.fetchall()
    if (len(results) == 0):
        return -1
    return results[0]['uid']


def getLastRequestInChannel(ruid, uid):
    """
    Gets the last request a user made for another user's channel.
    <ruid> - requesting user
    <uid> - receiving user
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT rid FROM requests WHERE ruid = %s AND uid = %s '
    query += 'ORDER BY timestamp DESC'
    cursor.execute(query, (ruid, uid,))
    rres = cursor.fetchone()
    if (rres is None):
        return -1
    return rres['rid']


def getUserByDisplayName(user):
    """
    Gets a uid and displayname from a given username
    <user> - DisplayName to match
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT uid, displayname FROM users '
    query += 'WHERE displayname LIKE %s'
    cursor.execute(query, [user, ])
    row = cursor.fetchone()
    return row


def setUserPassword(uid, pw):
    """
    Sets a given user's password.
    <uid> - User to update
    <pw> - Password (hashed!) to set.
    Returns number of affected users. One or zero, hopefully!
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE users SET password = %s WHERE uid = %s'
    cursor.execute(query, (pw, uid,))
    return cursor.rowcount


def getLoginUser(username):
    """
    Gets a user's login info given a UN and a password.
    <username> - Username (not displayname) **OR** email
    <password> - PW hash to match
    Returns the matching user or None
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT username, password, uid, displayname FROM users WHERE username = %s OR email = %s'
    cursor.execute(query, [username, username, ])
    user = cursor.fetchone()
    return user


def getStreamlabsUser(sluid):
    """
    Gets a user's userinfo given a StreamLabs UID
    <sluid> - StreamLabs ID to find a match for
    Returns a user object, or None
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT users.uid, username, signup, displayname, tuid, tname, sluid, slname, '
    query += 'userconf.allowanon, userconf.showreqname '
    query += 'FROM users '
    query += 'INNER JOIN userinfo ON userinfo.uid = users.uid '
    query += 'WHERE sluid = %s'
    cursor.execute(query, (sluid, ))
    row = cursor.fetchone()
    return row


def getTwitchUser(tuid):
    """
    Gets a user's userinfo given a Twitch UID
    <tuid> - Twitch ID to find a match for
    Returns a user object, or None
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT users.uid, username, signup, displayname, tuid, tname, sluid, slname, '
    query += 'userconf.allowanon, userconf.showreqname '
    query += 'FROM users '
    query += 'INNER JOIN userconf ON users.uid = userconf.uid '
    query += 'WHERE tuid = %s'
    cursor.execute(query, (tuid, ))
    row = cursor.fetchone()
    return row


def setSLUIDForUser(sluid, slname, uid):
    """
    Sets a StreamLabs ID for a given UID.
    <sluid> - StreamLabs ID to link to the user
    <slname> - StreamLabs displayname to link to the user
    <uid> - Local user to update
    Returns the number of changed rows (one or zero!)
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE users SET sluid = %s, slname = %s WHERE uid = %s'
    cursor.execute(query, (sluid, slname, uid))
    return cursor.rowcount


def setTUIDForUser(tuid, tname, uid):
    """
    Sets a Twitch ID for a given UID.
    <tuid> - Twitch ID to link to the user
    <tname> - Twitch displayname to link to the user
    <uid> - Local user to update
    Returns the number of changed rows (one or zero!)
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE users SET tuid = %s, tname = %s WHERE uid = %s'
    cursor.execute(query, (tuid, tname, uid))
    return cursor.rowcount


def getPasswordForUser(uid):
    """
    Returns the password hash for a user.
    <uid> - Local user to pull the password for.
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'SELECT password FROM users WHERE uid = %s'
    cursor.execute(query, (uid,))
    pw = cursor.fetchone()['password']
    return pw


def unlinkTwitch(uid):
    """
    Unlink a twitch account from a local account
    <uid> - local account to unlink
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE users SET tuid = 0, tname = "" WHERE uid = %s'
    cursor.execute(query, (uid,))
    return cursor.rowcount


def unlinkStreamlabs(uid):
    """
    Unlink a Streamlabs account from a local account
    <uid> - local account to unlink
    """
    cnx = getConnection()
    cursor = cnx.cursor(dictionary=True)
    query = 'UPDATE users SET sluid = 0, slname = "" WHERE uid = %s'
    cursor.execute(query, (uid,))
    return cursor.rowcount
