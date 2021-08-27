// DEBUG
const USERID = 1;
const APIURL = 'http://127.0.0.1:5000/api/v1';
// DEBUG

var songlist = []; // Holder for everything we get back

window.onload = function () {
    const req = new XMLHttpRequest();
    req.onload = function () {
        songlist = JSON.parse(this.responseText);
        writeSongList();
    };
    req.open('GET', APIURL + '/getpubsongs?uid=' + USERID);
    req.send();
};

function writeSongList() {
    let tblHtml = '<table class="table table-striped"><thead><tr>';
    tblHtml += '<th>Artist</th>';
    tblHtml += '<th>Title</th>';
    tblHtml += '<th>Play Count</th>';
    tblHtml += '<th>Last Played</th>';
    tblHtml += '<th></th>';
    tblHtml += '</tr></thead><tbody>';
    for (let i = 0; i < songlist.length; i++) {
        let song = songlist[i];
        tblHtml += '<tr>';
        tblHtml += '<td>' + song.artist.toString() + '</td>';
        tblHtml += '<td>' + song.title.toString() + '</td>';
        tblHtml += '<td class="text-center">' + song.plays.toString() + '</td>';
        tblHtml += '<td>' + song.lastplayed.toString() + '</td>';
        tblHtml += '<td><button data-artist="' + song.artist.toString() + '" data-title="' + song.title.toString() + '" data-id="' + song.slid + '" onclick="reqSong(this)">Request This Song</button></td>';
        tblHtml += '</tr>';
    }
    tblHtml += '</tbody></table>';
    document.getElementById('songlist').innerHTML = tblHtml;
}

function reqSong(e) {
    let slid = e.getAttribute('data-id');
    let artist = e.getAttribute('data-artist');
    let title = e.getAttribute('data-title');
    const req = new XMLHttpRequest();
    req.onload = function () {
        makeToast('Request', 'Your request for ' + title + ' by ' + artist + ' has been placed!');
    };
    req.open('GET', APIURL + '/addreq?uid=' + USERID + '&slid=' + slid);
    req.send();
}