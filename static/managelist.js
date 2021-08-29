var songlist = []; // Holder for everything we get back
var listOffset = 0;
var sort = 0;

const ARTIST = 1;
const TITLE = 2;
const PLAYS = 3;
const LAST = 4;
const PUB = 5;

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
    req.open('GET', APIURL + '/allsongs/' + uid);
    req.send();
}

function dosort(e) {
    let sorttype = e.getAttribute('data-field');
    switch (sorttype) {
        case 'artist':
            if (sort == ARTIST) {
                sort = -ARTIST;
                songlist.sort((b, a) => (a.artist.localeCompare(b.artist)));
            } else {
                sort = ARTIST;
                songlist.sort((a, b) => (a.artist.localeCompare(b.artist)));
            }
            break;
        case 'title':
            if (sort == TITLE) {
                sort = -TITLE;
                songlist.sort((b, a) => (a.title.localeCompare(b.title)));
            } else {
                sort = TITLE;
                songlist.sort((a, b) => (a.title.localeCompare(b.title)));
            }
            break;
        case 'plays':
            if (sort == PLAYS) {
                sort = -PLAYS;
                songlist.sort((b, a) => (a.plays < b.plays ? 1 : -1));
            } else {
                sort = PLAYS;
                songlist.sort((a, b) => (a.plays < b.plays ? 1 : -1));
            }
            break;
        case 'last':
            if (sort == LAST) {
                sort = -LAST;
                songlist.sort((b, a) => (b.lastplayed < a.lastplayed ? 1 : -1));
            } else {
                sort = LAST;
                songlist.sort((b, a) => (a.lastplayed < b.lastplayed ? 1 : -1));
            }
            break;
        case 'pub':
            if (sort == PUB) {
                sort = -PUB;
                songlist.sort((b, a) => ((a.public === b.public) ? 0 : a.public?-1:1));
            } else {
                sort = PUB;
                songlist.sort((a, b) => ((a.public === b.public) ? 0 : a.public?-1:1));
            }
            break;
    }
    writeSongList();
}

function writeSongList() {
    let tblHtml = '<table class="table table-secondary table-hover table-striped"><thead><tr>';
    tblHtml += '<th style="width: 20%" data-field="artist" onclick="dosort(this)">Artist';
    if (sort == -1) { tblHtml += ' ▼'; } 
    if (sort == 1) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 20%" data-field="title" onclick="dosort(this)">Title';
    if (sort == -2) { tblHtml += ' ▼'; } 
    if (sort == 2) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 10%" data-field="plays" onclick="dosort(this)">Play Count';
    if (sort == -3) { tblHtml += ' ▼'; } 
    if (sort == 3) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 20%" data-field="last" onclick="dosort(this)">Last Played';
    if (sort == -4) { tblHtml += ' ▼'; } 
    if (sort == 4) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 10%" data-field="pub" onclick="dosort(this)">Published';
    if (sort == -5) { tblHtml += ' ▼'; } 
    if (sort == 5) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 20%"></th>';
    tblHtml += '</tr></thead><tbody>';
    let maxLength = Math.min(songlist.length, listOffset + 10);
    let curPage = Math.ceil(listOffset / 10) + 1;
    let lastPage = Math.ceil(songlist.length / 10);
    for (let i = listOffset; i < maxLength; i++) {
        let song = songlist[i];
        tblHtml += '<tr>';
        tblHtml += '<td>' + song.artist.toString() + '</td>';
        tblHtml += '<td>' + song.title.toString() + '</td>';
        tblHtml += '<td class="text-center">' + song.plays.toString() + '</td>';
        tblHtml += '<td>' + (song.lastplayed || "Never").toString() + '</td>';
        tblHtml += '<td><input type="checkbox" ';
        if (song.public) { tblHtml += 'checked '; }
        tblHtml += '/></td><td>';
        tblHtml += '<button style="margin: 2%;" class="btn btn-secondary" data-id="' + song.slid + '" onclick="editSong(this)">✎ Edit</button>';
        tblHtml += '<button style="margin: 2%;" class="btn btn-danger" data-title="' + song.title + '" data-id="' + song.slid + '" onclick="deleteSong(this)">✖ Remove</button>';
        tblHtml += '</td></tr>';
    }
    tblHtml += '<td colspan=5>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button type="button" onclick="firstPage();" class="btn btn-secondary">« First Page</button>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button type="button" onclick="prevPage();" class="btn btn-secondary">‹ Prev Page</button>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<span>' + curPage.toString() + ' / ' + lastPage.toString() + '</span>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button type="button" onclick="nextPage();" class="btn btn-secondary">Next Page ›</button>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button type="button" onclick="lastPage();" class="btn btn-secondary">Last Page »</button></td>';
    tblHtml += '</span>';
    tblHtml += '<td><button onclick="addSong(this)">Add Song</button></td>';
    tblHtml += '</tbody></table>';
    document.getElementById('songlist').innerHTML = tblHtml;
}

function firstPage() {
    listOffset = 0;
    writeSongList();
}
function prevPage() {
    listOffset -= 10;
    if (listOffset < 0) { listOffset = 0; }
    writeSongList();
}
function nextPage() {
    listOffset += 10;
    if (listOffset > songlist.length) { listOffset = songlist.length - 10; }
    writeSongList();
}
function lastPage() {
    listOffset = songlist.length - 10;
    writeSongList();
}

function deleteSong(e) {
    let slid = { slid: e.getAttribute('data-id'), };
    let title = e.getAttribute('data-title');
    $.ajax({
        type: 'POST',
        url: APIURL + '/delsong',
        data: JSON.stringify(slid),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function (msg) {
            if (msg.status == 200) {
                makeToast('Success', title + ' has been removed from your list.');
                loadList();
            } else {
                makeToast('Error', title + ' could not be removed from your list.');
            }
        }
    });
}


function saveSong(e) {
    let published = document.getElementById('addsongpublic').checked;
    let newSong = {
        title: $('#addsongtitle').val(),
        artist: $('#addsongartist').val(),
        link: $('#addsonglink').val(),
        pub: published ? 1 : 0,
        uid: uid,
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
                makeToast('Success', 'Your song has been added successfully!');
                loadList();
            } else {
                // OH CRAP EVERYTHING IS ON FIRE
            }
        }
    });
}

/*
function editSong(e) {
    let slid = e.getAttribute('data-id');
    const req = new XMLHttpRequest();
    req.onload = function () {
        alert("Aight");
    };
    req.open('GET', APIURL + '/addreq?uid=' + USERID + '&slid=' + slid);
    req.send();
}
*/

function addSong(e) {
    $('#addSongModal').modal('show');
}

