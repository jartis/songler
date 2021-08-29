var songlist = []; // Holder for everything we get back
var listOffset = 0;

window.onload = function () {
    const req = new XMLHttpRequest();
    req.onload = function () {
        songlist = JSON.parse(this.responseText);
        writeSongList();
    };
    if (uid == listuid) {
        // Get ALL the songs for onesself.
        // TODO: Mark this somehow
        req.open('GET', APIURL + '/allsongs/' + uid);
    } else {
        req.open('GET', APIURL + '/getpubsongs?uid=' + listuid);
    }
    req.send();
};

function writeSongList() {
    let tblHtml = '<table class="table table-secondary table-striped"><thead><tr>';
    tblHtml += '<th style="width: 20%">Artist</th>';
    tblHtml += '<th style="width: 20%">Title</th>';
    tblHtml += '<th style="width: 20%">Play Count</th>';
    tblHtml += '<th style="width: 20%">Last Played</th>';
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
        tblHtml += '<td>' + (song.lastplayed == null ? 'Never' : song.lastplayed.toString()) + '</td>';
        tblHtml += '<td><button data-artist="' + song.artist.toString() + '" data-title="' + song.title.toString() + '" data-id="' + song.slid + '" onclick="reqSong(this)">Request This Song</button></td>';
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
    req.open('GET', APIURL + '/addreq?slid=' + slid);
    req.send();
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