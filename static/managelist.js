var songlist = []; // Holder for everything we get back
var listOffset = 0;

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

function writeSongList() {
    let tblHtml = '<table class="table table-secondary table-hover table-striped"><thead><tr>';
    tblHtml += '<th style="width: 20%">Artist</th>';
    tblHtml += '<th style="width: 20%">Title</th>';
    tblHtml += '<th style="width: 10%">Play Count</th>';
    tblHtml += '<th style="width: 20%">Last Played</th>';
    tblHtml += '<th style="width: 10%">Published</th>';
    tblHtml += '<th style="width: 20%"></th>';
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
        tblHtml += '/></td>';
        tblHtml += '<td><button data-id="' + song.slid + '" onclick="editSong(this)">Edit Song</button></td>';
        tblHtml += '</tr>';
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

function firstPage(){
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
                writeSongList();
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

