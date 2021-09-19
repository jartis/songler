from flask import Blueprint, render_template, g, session
from conf import *
from dbutil import *

route_blueprint = Blueprint('route_blueprint', __name__)

@route_blueprint.route('/login')
def renderLogin():
    """
    Shows the login page.
    """
    return render_template('login.jinja')


@route_blueprint.route('/newuser')
def newuser():
    """
    Shows the Create (native) User page
    """
    return render_template('newuser.jinja')


@route_blueprint.route('/wheel')
def renderWheel():
    """
    Shows the current logged-in user's overlay page.
    """
    if g.uid is None:
        return render_template('error.jinja', error=("You must be logged in to view your overlay"))
    return render_template('wheel.jinja')


@route_blueprint.route('/')
@route_blueprint.route('/home')
def renderHome():
    """
    Shows the homepage.
    """
    return render_template('home.jinja')


@route_blueprint.route('/songlist/<user>', methods=['GET', ])
def showSongList(user):
    """
    Shows the public songlist for a given user.
    <user> - The *Display Name* for the songlist we want to display.
    """
    user = str(user)
    userinfo = getUserByDisplayName(user)
    if userinfo is not None:
        uid = int(userinfo['uid'])
        username = userinfo['displayname']
        return render_template('requestlist.jinja', listuid=uid, listuser=username)
    else:
        return render_template('error.jinja', error=("No user found with the name " + user))


@route_blueprint.route('/managelist', methods=['GET', ])
def manageSongList():
    """
    Shows the song list manager / editor for the current logged in user.
    """
    if int(g.uid) > 0:
        return render_template('managelist.jinja')
    else:
        return render_template('error.jinja', error=("No songlist found for user " + g.username))

@route_blueprint.route('/requests', methods=['GET',])
def manageRequests():
    """
    Shows the request list manager for the current logged in user.
    """
    if int(g.uid) > 0:
        return render_template('managereqs.jinja')
    else:
        return render_template('error.jinja', error=("No request list found for user " + g.username))

@route_blueprint.route('/profile/<user>', methods=['GET', ])
def renderProfile(user):
    """
    Gets the profile page for the specified user.
    <user> - *Display Name* for the profile page to retrieve.
    """
    user = str(user)
    row = getUserByDisplayName(user)
    if row is not None:
        uid = int(row['uid'])
        return render_template('profile.jinja', listuid=uid, listuser=user)
    else:
        return render_template('error.jinja', error=("No user found with the name " + user))


@route_blueprint.route('/editprofile', methods=['GET', ])
def editProfile():
    """
    Edits the profile of the currently logged in user.
    Errors out if no session stuff is set.
    """
    if (g.uid == 0):
        return render_template('error.jinja', error=("You must be logged in to edit your profile."))
    return render_template('editprofile.jinja')


@route_blueprint.route('/song/<sid>', methods=['GET', ])
def songInfo(sid):
    """
    Gets a song's "Profile Page".
    <sid> - Song ID for the relevant song.
    """
    sid = int(sid)
    return render_template('song.jinja', sid=sid)


@route_blueprint.route('/artist/<aid>', methods=['GET', ])
def artistInfo(aid):
    """
    Gets an artist's "Profile Page".
    <aid> - Artist ID for the relevant song.
    """
    aid = int(aid)
    return render_template('artist.jinja', aid=aid)


@route_blueprint.route('/reqs/', methods=['GET',])
def minReqs():
    """
    Minimal version of the requests page, suitable for overlays
    """
    if int(g.uid) > 0:
        return render_template('minreqs.jinja')
    else:
        return render_template('error.jinja', error=("No request list found for user " + g.username))
