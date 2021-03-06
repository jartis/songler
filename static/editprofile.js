var userinfo = {};

window.onload = function () {
    const req = new XMLHttpRequest();
    req.onload = function () {
        userinfo = JSON.parse(this.responseText);
        writeUserInfo();
        $('#password').passtrength();
        $('#passwordconf').passtrength();
        document.getElementById('password').addEventListener('input', checkPass);
        document.getElementById('passwordconf').addEventListener('input', checkPass);
        document.getElementById('displayName').addEventListener('change', setDisplayName);
        document.getElementById('reqnames').addEventListener('change', setShowReqName);
        document.getElementById('anon').addEventListener('change', setAnon);
        document.getElementById('offline').addEventListener('change', setOffline);
        $('form').submit(false);
    };
    req.open('GET', APIURL + '/userinfo/' + uid);
    req.send();
};

function checkPass() {
    if (document.getElementById('password').value ==
        document.getElementById('passwordconf').value) {
        document.getElementById('changepassbtn').disabled = false;
    } else {
        document.getElementById('changepassbtn').disabled = true;
    }
}

function writeUserInfo() {
    // Member since:
    let pt = '';
    pt += '<form class="form-signin">';
    pt += '<p>Member since ';
    pt += new Intl.DateTimeFormat('en').format(Date.parse(userinfo.signup));
    pt += '</p>';
    pt += '<p>Display Name: ';
    pt += '<input type="text" name="displayName" id="displayName"></p>';
    if (Number(userinfo.tuid) > 0) {
        pt += `<p>Linked Twitch user: <a href="https://twitch.tv/${userinfo.tname}">${userinfo.tname}</a></p>`;
        pt += '<p><button onclick="unlinkTwitch();" class="btn btn-danger">Unlink Twitch account</button></p>';
    } else {
        pt += '<p><button onclick="linkTwitch();" class="btn btn-primary">Connect your Twitch account</button></p>';
    }
    if (Number(userinfo.sluid) > 0) {
        pt += `<p>Linked Streamlabs user: ${userinfo.slname}</p>`;
        pt += '<p><button onclick="unlinkStreamlabs();" class="btn btn-danger">Unlink Streamlabs account</button></p>';
    } else {
        pt += '<p><button onclick="linkStreamlabs();" class="btn btn-primary">Connect your Streamlabs account</button></p>';
    }
    // PW stuff
    pt += '<div class="form-group">';
    pt += '<label for="password">Password</label>';
    pt += '<input type="password" class="form-control" name="password" id="password" placeholder="" required></div>';
    pt += '<div class="form-group">';
    pt += '<label for="passwordconf">Confirm Password</label>';
    pt += '<input type="password" class="form-control" name="passwordconf" id="passwordconf" placeholder="" required>';
    pt += '<button id="changepassbtn" class="btn btn-danger" onclick="savePassword();" disabled>Save Password</button>';
    pt += '</div></form><hr>';
    pt += '<form class="form-signin">';
    pt += '<h4>Configuration Options</h4>';
    pt += '<div class="form-group">';
    pt += '<label for="reqnames">Show requester names in queue:</label>';
    pt += '<div class="text-center form-check form-switch"><input class="form-check-input" id="reqnames" name="reqnames" type="checkbox"/></div>';
    pt += '<div class="form-group">';
    pt += '<label for="anon">Allow anonymous requests:</label>';
    pt += '<div class="text-center form-check form-switch"><input class="form-check-input" id="anon" name="anon" type="checkbox"/></div>';
    pt += '<div class="form-group">';
    pt += '<label for="offline">Allow offline requests:</label>';
    pt += '<div class="text-center form-check form-switch"><input class="form-check-input" id="offline" name="offline" type="checkbox"/></div>';

    pt += '</form>';

    document.getElementById('userinfo').innerHTML = pt;
    document.getElementById('profilename').innerText = 'Edit Profile for ' + userinfo.username;
    document.getElementById('displayName').value = userinfo.displayname;
    document.getElementById('reqnames').checked = (userinfo.showreqname == 1);
    document.getElementById('anon').checked = (userinfo.allowanon == 1);
    document.getElementById('offline').checked = (userinfo.allowoffline == 1);
}

function unlinkTwitch() {
    window.location = '/tunlink';
}

function linkTwitch() {
    window.location = '/tlink';
}

function linkStreamlabs() {
    window.location = '/sllink';
}

function unlinkStreamlabs() {
    window.location = '/slunlink';
}

function setShowReqName() {
    let doShow = {
        show: (document.getElementById('reqnames').checked ? 1 : 0),
    };
    $.ajax({
        type: 'POST',
        url: APIURL + '/setshowreq',
        data: JSON.stringify(doShow),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function(msg) {
            if (msg.responseText == '1') {
                makeToast(SUCCESS, '?????? Success', 'Your overlays will show requester names.');
            } else if (msg.responseText == '0') {
                makeToast(SUCCESS, '?????? Success', 'Your overlays will hide requester names.');
            } else {
                makeToast(ERROR, '?????? Error', 'Error setting "Show Requester Names" option.');
            }
        }
    });
}

function setAnon() {
    let doAnon = {
        anon: (document.getElementById('anon').checked ? 1 : 0),
    };
    $.ajax({
        type: 'POST',
        url: APIURL + '/setanon',
        data: JSON.stringify(doAnon),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function(msg) {
            if (msg.responseText == '1') {
                makeToast(SUCCESS, '?????? Success', 'Anonymous requests are enabled.');
            } else if (msg.responseText == '0') {
                makeToast(SUCCESS, '?????? Success', 'Anonymous requests are disabled.');
            } else {
                makeToast(ERROR, '?????? Error', 'Error setting "Anonymous Request" option.');
            }
        }
    });
}

function setOffline() {
    let doOffline = {
        allowoffline: (document.getElementById('offline').checked ? 1 : 0),
    };
    $.ajax({
        type: 'POST',
        url: APIURL + '/setallowoffline',
        data: JSON.stringify(doOffline),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function(msg) {
            if (msg.responseText == '1') {
                makeToast(SUCCESS, '?????? Success', 'Offline requests are enabled.');
            } else if (msg.responseText == '0') {
                makeToast(SUCCESS, '?????? Success', 'Offline requests are disabled.');
            } else {
                makeToast(ERROR, '?????? Error', 'Error setting "Offline Requests" option.');
            }
        }
    });
}

function setDisplayName() {
    let dName = {
        dname: document.getElementById('displayName').value,
    };
    $.ajax({
        type: 'POST',
        url: APIURL + '/setdisplayname',
        data: JSON.stringify(dName),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function(msg) {
            if (msg.responseText == 'OK') {
                makeToast(SUCCESS, '?????? Success', 'Your display name was updated!');
            } else if (msg.responseText == 'NG') {
                makeToast(ERROR, '?????? Error', 'This display name is already in use.');
            } else {
                makeToast(ERROR, '?????? Error', 'There was an error updating your display name.');
            }
        }
    });
}

function savePassword() {
    // Do this later
    let postData = {
        password: document.getElementById('password').value,
    };
    $.ajax({
        type: 'POST',
        url: APIURL + '/savepass',
        data: JSON.stringify(postData),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function(msg) {
            if (msg.responseText == 'OK') {
                makeToast(SUCCESS, '?????? Success', 'Your password was updated!');
                document.getElementById('password').value = '';
                document.getElementById('passwordconf').value = '';
            } else {
                makeToast(ERROR, '?????? Error', 'Your password could not be changed.');
                document.getElementById('password').value = '';
                document.getElementById('passwordconf').value = '';
            }
        }
    });
}