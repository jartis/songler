// DEBUG
const USERID = 1;
const APIURL = 'http://127.0.0.1:5000/api/v1';
// DEBUG

var songlist = []; // Holder for everything we get back

window.onload = function () {
    $('#addSongModal').modal();
    loadList();
};

function loadList() {
    const req = new XMLHttpRequest();
    req.onload = function () {
        songlist = JSON.parse(this.responseText);
        writeSongList();
    };
    req.open('GET', APIURL + '/songlist?uid=' + USERID);
    req.send();
}

function writeSongList() {
    let tblHtml = '<table class="table table-striped table-dark"><thead><tr>';
    tblHtml += '<th>Artist</th>';
    tblHtml += '<th>Title</th>';
    tblHtml += '<th>Play Count</th>';
    tblHtml += '<th>Last Played</th>';
    tblHtml += '<th>Published</th>';
    tblHtml += '<th></th>';
    tblHtml += '</tr></thead><tbody>';
    for (let i = 0; i < songlist.length; i++) {
        let song = songlist[i];
        tblHtml += '<tr>';
        tblHtml += '<td>' + song.artist.toString() + '</td>';
        tblHtml += '<td>' + song.title.toString() + '</td>';
        tblHtml += '<td class="text-center">' + song.plays.toString() + '</td>';
        tblHtml += '<td>' + (song.lastplayed || "Never").toString() + '</td>';
        tblHtml += '<td><input type="checkbox" disabled ';
        if (song.public) { tblHtml += 'checked '; }
        tblHtml += '/></td>';
        tblHtml += '<td><button data-id="' + song.slid + '" onclick="reqSong(this)">Edit Song</button></td>';
        tblHtml += '</tr>';
    }
    tblHtml += '<td colspan=5></td><td><button onclick="addSong(this)">Add Song</button></td>';
    tblHtml += '</tbody></table>';
    document.getElementById('songlist').innerHTML = tblHtml;
}

function saveSong(e) {
    let published = document.getElementById('songpublic').checked;
    let newSong = {
        title: $('#songtitle').val(),
        artist: $('#songartist').val(),
        pub: published ? 1 : 0,
        uid: USERID,
    };

    $.ajax({
        type: 'POST',
        url: APIURL + '/addsong',
        data: JSON.stringify(newSong),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function (msg) {
            if (msg.status == 200) {
                $('#addSongModal').modal('hide');
                alert('Song saved successfully!');
            } else {
                // OH CRAP EVERYTHING IS ON FIRE
            }
        }
    });
}

function reqSong(e) {
    let slid = e.getAttribute('data-id');
    const req = new XMLHttpRequest();
    req.onload = function () {
        alert("Aight");
    };
    req.open('GET', APIURL + '/addreq?uid=' + USERID + '&slid=' + slid);
    req.send();
}

function addSong(e) {
    console.log("Not yet...");
    $('#addSongModal').modal('show');
}

