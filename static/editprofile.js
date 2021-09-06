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
        document.getElementById('reqnames').addEventListener('change', setShowReqNames);
        document.getElementById('anon').addEventListener('change', setAnon);
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
        pt += `<p>Linked Twitch user: <a href="https://twitch.tv/${userinfo.twitchname}">${userinfo.twitchname}</a></p>`;
        pt += '<p><button onclick="unlinkTwitch();" class="btn btn-danger">Unlink Twitch account</button></p>';
        // You *HAVE* a twitch account, wanna unlink it?
    } else {
        // You *DON'T* have your twitch linked, U WAN?
        pt += '<p><button onclick="linkTwitch();" class="btn btn-primary">Connect your Twitch account</button></p>';
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
    pt += '</form>';

    document.getElementById('userinfo').innerHTML = pt;
    document.getElementById('profilename').innerText = 'Edit Profile for ' + userinfo.username;
    document.getElementById('displayName').value = userinfo.displayname;
    document.getElementById('reqnames').checked = (userinfo.showreqnames == 1);
    document.getElementById('anon').checked = (userinfo.showreqnames == 1);
}

function unlinkTwitch() {
    window.location = '/tunlink';
}

function linkTwitch() {
    window.location = '/tlink';
}

function setShowReqNames() {
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
            if (msg.responseText == 'Y') {
                makeToast(SUCCESS, '✔️ Success', 'Your overlays will show requester names.');
            } else if (msg.responseText == 'N') {
                makeToast(SUCCESS, '✔️ Success', 'Your overlays will hide requester names.');
            } else {
                makeToast(ERROR, '⚠️ Error', 'Your overlays will do whatever they feel like.');
            }
        }
    });
}

function setAnon() {
    let doShow = {
        show: (document.getElementById('anon').checked ? 1 : 0),
    };
    $.ajax({
        type: 'POST',
        url: APIURL + '/setanon',
        data: JSON.stringify(doShow),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function(msg) {
            if (msg.responseText == 'Y') {
                makeToast(SUCCESS, '✔️ Success', 'Anonymous requests are enabled.');
            } else if (msg.responseText == 'N') {
                makeToast(SUCCESS, '✔️ Success', 'Anonymous requests are disabled.');
            } else {
                makeToast(ERROR, '⚠️ Error', 'Anonymous requests are...?');
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
        url: APIURL + '/setname',
        data: JSON.stringify(dName),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function(msg) {
            if (msg.responseText == 'OK') {
                makeToast(SUCCESS, '✔️ Success', 'Your display name was updated!');
            } else if (msg.responseText == 'NG') {
                makeToast(ERROR, '⚠️ Error', 'This display name is already in use.');
            } else {
                makeToast(ERROR, '⚠️ Error', 'There was an error updating your display name.');
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
                makeToast(SUCCESS, '✔️ Success', 'Your password was updated!');
                document.getElementById('password').value = '';
                document.getElementById('passwordconf').value = '';
            } else {
                makeToast(ERROR, '⚠️ Error', 'Your password could not be changed.');
                document.getElementById('password').value = '';
                document.getElementById('passwordconf').value = '';
            }
        }
    });
}