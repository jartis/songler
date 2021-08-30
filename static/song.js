var songinfo = {};

window.onload = function () {
    const req = new XMLHttpRequest();
    req.onload = function () {
        songinfo = JSON.parse(this.responseText);
        writeSongInfo();
    };
    req.open('GET', APIURL + '/songinfo/' + sid);
    // }
    req.send();
};

function writeSongInfo() {
    document.getElementById('headline').innerText = songinfo.title + ' by ' + songinfo.artist;
    let si = '';
    si += '<p>Total plays: ' + songinfo.plays + '</p>'
    // Who has this on their songlist?
    if (songinfo.users.length > 0) {
        si += '<h3>Users that play ' + songinfo.title + ':</h3>';
        for (let i = 0; i < songinfo.users.length; i++) {
            si += '<p><a href="/songlist/' + songinfo.users[i].username + '">' + songinfo.users[i].username + '</a></p>';
        }
    }
    document.getElementById('songinfo').innerHTML = si;
}