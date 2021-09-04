var userinfo = {};

window.onload = function() {
    const req = new XMLHttpRequest();
    req.onload = function () {
        userinfo = JSON.parse(this.responseText);
        writeUserInfo();
    };
    req.open('GET', APIURL + '/userinfo/' + listuid);
    req.send();
};

function writeUserInfo() {
    // Member since:
    let pt = '';
    pt += '<p>Member since ';
    pt += new Intl.DateTimeFormat('en').format(Date.parse(userinfo.signup));
    pt += '</p>';
    // Public songlist link:
    pt += '<p><a href="/songlist/' + userinfo.username + '">Public song list for ' + userinfo.username + '</a></p>';
    // Twitch link:
    if (userinfo.twitch != '0') {
        pt += '<p><a href="https://twitch.tv/' + userinfo.username + '">' + userinfo.username + ' on Twitch</a></p>';
    }
    document.getElementById('userinfo').innerHTML = pt;
    document.getElementById('profilename').innerText = 'User Profile for ' + userinfo.username;
}