from app import db


def setSongWheel(wheel, slid, uid):
    """
    Sets the 'wheel' column to true or false for the given songlist ID.
    <wheel> - True or False for the 'show on wheel' value
    <slid> - Songlist ID 
    <uid> - UID making the change. If this doesn't match the SLID owner, don't change. 
    """
    cursor = db.connection.cursor()
    query = 'UPDATE songlists SET wheel = %s WHERE slid = %s AND uid = %s'
    cursor.execute(query, (wheel, slid, uid,))
    return cursor.rowcount


def setSongWheel(pub, slid, uid):
    """
    Sets the 'public' column to true or false for the given songlist ID.
    <pub> - True or False for the 'show on public list' value
    <slid> - Songlist ID 
    <uid> - UID making the change. If this doesn't match the SLID owner, don't change. 
    """
    cursor = db.connection.cursor()
    query = 'UPDATE songlists SET public = %s WHERE slid = %s AND uid = %s'
    cursor.execute(query, (pub, slid, uid,))
    return cursor.rowcount


def getAllArtistsAndTitlesAndSids():
    """
    Gets a JSON array of all {artist, title, sid} in songs.
    """
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
    query = 'DELETE FROM songlists WHERE slid = %s AND uid = %s'
    cursor.execute(query, (slid, uid,))
    return cursor.rowcount


def getAllTitles():
    """
    Get a raw list of titles and tids for populating autocomplete box.
    """
    cursor = db.connection.cursor()
    query = 'SELECT title, tid FROM titles'
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getAllArtists():
    """
    Get a raw list of artists and aids for populating autocomplete box.
    """
    query = 'SELECT artist, aid FROM artists'
    cursor = db.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getUserDisplayNames():
    """
    Get a raw list of user displaynames for populating autocomplete box.
    """
    query = 'SELECT displayname FROM users'
    cursor = db.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def getSongArtistTitle(sid):
    """
    Gets an {artist, title} from the songlist given a sid
        # TODO: Handle a 'None' case gracefully

    """
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
    query = 'SELECT timestamp FROM plays '
    query += 'WHERE sid = %s ORDER BY timestamp DESC'
    cursor.execute(query, (int(sid),))
    result = int(cursor.fetchone()['timestamp'])
    return result


def setDisplayName(dname, uid):
    """
    Sets the display name for the specified user.
    <dname> - New displayname for specified user
    <uid> - UID to update the displayname
    Returns number of rows updated - 0 for no matching UID / error
    """
    cursor = db.connection.cursor()
    query = 'UPDATE users SET displayname = %s where uid = %s'
    cursor.execute(query, (dname, uid,))
    return cursor.rowcount


def getAnon(uid):
    """
    Returns the "Allow anonymous requests" config value for the specified user.
    <uid> - User to get the Anon flag for
    """
    cursor = db.connection.cursor()
    query = 'SELECT anon FROM users WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    return str(result['anon'])


def setAnon(uid, anon):
    """
    Sets the "Allow Anonymous Requests" config value for the specified user.
    <uid> - User to set the Anon flag for
    <anon> - Value to set the Anon flag
    """
    cursor = db.connection.cursor()
    query = 'UPDATE users SET anon = %s WHERE uid = %s'
    cursor.execute(query, (anon, uid,))
    return cursor.rowcount


def getShowNames(uid):
    """
    Returns the "Show Requester Names" config value for the specified user.
    <uid> - User to get the ShowNames flag for
    """
    cursor = db.connection.cursor()
    query = 'SELECT showreqnames FROM users WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()
    return str(result['showreqnames'])


def setShowNames(uid, show):
    """
    Sets the "Show Requester Names" config value for the specified user.
    <uid> - User to set the ShowNames flag for
    <show> - Value to set the ShowNames flag
    """
    cursor = db.connection.cursor()
    query = 'UPDATE users SET showreqnames = %s WHERE uid = %s'
    cursor.execute(query, (show, uid,))
    return cursor.rowcount


def getArtistInfo(aid):
    """
    Gets {artist} name for a specific aid.
    <aid> - Artist ID to get the name for.
    """
    cursor = db.connection.cursor()
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


def findSongOnUserSonglist(sid, uid):
    """
    Finds any entries for a song already existing on a user's songlist.
    <sid> - Song ID to find on the list
    <uid> - User ID for the list to search
    Returns the count of entries matching the sid on the user's list.
    """
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
    if (ruid > 0):
        query = 'SELECT rid, uid FROM requests WHERE ruid = %s AND uid IN '
        query += '(SELECT uid FROM songlists WHERE slid = %s)'
        cursor.execute(query, (ruid, slid,))
        result = cursor.fetchall()
        if (len(result) > 0):
            if (int(result['uid']) != int(ruid)):
                # Only bail out if the song owner isn't the one requesting. You can fill your own queue.
                return False
    return True


def addRequest(ruid, rname, prio, slid):
    """
    Adds a request object to the MQ
    <ruid> - Requesting user's UID
    <rname> - Requesting user's displayname
    <prio> - Priority to set for the request
    <slid> - Songlist ID to add a request for
    Returns count of added rows - 0 for no matches, 1 for success
    """
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
    query = 'SELECT COUNT(*) as count FROM requests '
    query += 'WHERE uid = %s'
    cursor.execute(query, (uid,))
    result = cursor.fetchone()['count']
    return result


def getUserInfo(uid):
    """
    Returns the {uid, username, signup, displayname, tuid, 
    tname, sluid, slname, anon, showreqnames} info for the specified user.
    <uid> - The user ID to pull the userinfo for
    """
    cursor = db.connection.cursor()
    query = 'SELECT uid, username, signup, displayname, tuid, tname, sluid, slname, anon, showreqnames '
    query += 'FROM users WHERE uid = %s'
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
    cursor = db.connection.cursor()
    query =  'SELECT songlists.slid, artists.artist, titles.title, songlists.public, '
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
    cursor = db.connection.cursor()
    query = 'SELECT slid FROM requests WHERE requests.rid = %s'
    cursor.execute(query, (rid,))
    result = cursor.fetchone()
    return int(result['slid'])


def playSong(slid, date = ''):
    """
    Add a "play" for a songlist ID
    <slid> - Songlist entry to update
    """
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
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
    cursor = db.connection.cursor()
    query = 'SELECT rid FROM requests WHERE ruid = %s AND uid = %s '
    query += 'ORDER BY timestamp DESC'
    cursor.execute(query, (ruid, uid,))
    rres = cursor.fetchone()
    if (rres is None):
        return -1
    return rres['rid']
