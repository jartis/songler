var songlist = []; // Holder for everything we get back
var listOffset = 0;
var sort = 0;

const ARTIST = 1;
const TITLE = 2;
const PLAYS = 3;
const LAST = 4;

window.onload = function () {
    const req = new XMLHttpRequest();
    req.onload = function () {
        songlist = JSON.parse(this.responseText);
        writeSongList();
    };
    req.open('GET', APIURL + '/getpubsongs/' + listuid);
    req.send();
};

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
    }
    writeSongList();

}

function writeSongList() {
    let tblHtml = '<table class="table align-middle table-secondary table-striped"><thead><tr>';
    tblHtml += '<th style="width: 20%" data-field="artist" onclick="dosort(this)">Artist';
    if (sort == -1) { tblHtml += ' ▼'; }
    if (sort == 1) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 20%" data-field="title" onclick="dosort(this)">Title';
    if (sort == -2) { tblHtml += ' ▼'; }
    if (sort == 2) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 20%" data-field="plays" onclick="dosort(this)">Play Count';
    if (sort == -3) { tblHtml += ' ▼'; }
    if (sort == 3) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 20%" data-field="last" onclick="dosort(this)">Last Played';
    if (sort == -4) { tblHtml += ' ▼'; }
    if (sort == 4) { tblHtml += ' ▲'; }
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
        let lp = 'Never';
        let lpd = Date.parse(song.lastplayed);
        if (song.lastplayed) { lp = new Intl.DateTimeFormat('en').format(lpd); }
        tblHtml += '<td>' + lp + '</td>';
        tblHtml += '<td><button class="btn btn-sm btn-secondary" data-artist="' + song.artist.toString() + '" data-title="' + song.title.toString() + '" data-id="' + song.slid + '" onclick="reqSong(this)">Request This Song</button></td>';
        tblHtml += '</tr>';
    }
    tblHtml += '<td colspan=5>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button id="fp" type="button" onclick="firstPage();" class="btn btn-secondary">« First Page</button>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button id="pp" type="button" onclick="prevPage();" class="btn btn-secondary">‹ Prev Page</button>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<span>' + curPage.toString() + ' / ' + lastPage.toString() + '</span>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button id="np" type="button" onclick="nextPage();" class="btn btn-secondary">Next Page ›</button>';
    tblHtml += '</span>';
    tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
    tblHtml += '<button id="lp" type="button" onclick="lastPage();" class="btn btn-secondary">Last Page »</button></td>';
    tblHtml += '</span>';
    tblHtml += '</tbody></table>';
    document.getElementById('songlist').innerHTML = tblHtml;
}

function fixPageButtons() {
    $("fp").hide();
    $("pp").hide();
    $("np").hide();
    $("lp").hide();
    if (listOffset > 0) { $("fp").show(); $("pp").show(); }
    if (listOffset < songlist.length - 10) { $("np").show(); $("lp").show(); }
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

function reqSong(e) {
    let slid = e.getAttribute('data-id');
    let artist = e.getAttribute('data-artist');
    let title = e.getAttribute('data-title');
    const req = new XMLHttpRequest();
    req.onload = function () {
        if (this.responseText == 'QF') {
            makeToast(ERROR, '⚠️ Error', 'You already have a request in the queue for this user.');
        } else if (this.responseText == 'OK') {
            makeToast(SUCCESS, '✔️ Success', 'Your request for ' + title + ' by ' + artist + ' has been placed!');
        } else {
            makeToast(ERROR, '⚠️ Error', 'Something weird happened...');
        }
    };
    req.open('GET', APIURL + '/addreq/' + slid);
    req.send();
}