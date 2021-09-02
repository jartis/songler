var songlist = []; // Holder for everything we get back
var listOffset = 0;
var sort = 0;

const ARTIST = 1;
const TITLE = 2;
const PLAYS = 3;
const LAST = 4;
const PUB = 5;
const WHEEL = 6;

window.onload = function () {
    $('#addSongModal').modal();
    loadList();
    makeSongBoxesAutoComplete();
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
            case 'wheel':
                if (sort == WHEEL) {
                    sort = -WHEEL;
                    songlist.sort((b, a) => ((a.wheel === b.wheel) ? 0 : a.wheel?-1:1));
                } else {
                    sort = WHEEL;
                    songlist.sort((a, b) => ((a.wheel === b.wheel) ? 0 : a.wheel?-1:1));
                }
                break;
    }
    writeSongList();
}

function writeSongList() {
    let tblHtml = '<table class="table table-secondary table-hover align-middle table-striped"><thead><tr>';
    tblHtml += '<th style="width: 20%" data-field="artist" onclick="dosort(this)">Artist';
    if (sort == -1) { tblHtml += ' ▼'; } 
    if (sort == 1) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 20%" data-field="title" onclick="dosort(this)">Title';
    if (sort == -2) { tblHtml += ' ▼'; } 
    if (sort == 2) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 5%" data-field="plays" onclick="dosort(this)">Plays';
    if (sort == -3) { tblHtml += ' ▼'; } 
    if (sort == 3) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 10%" data-field="last" onclick="dosort(this)">Last Played';
    if (sort == -4) { tblHtml += ' ▼'; } 
    if (sort == 4) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 5%" data-field="pub" onclick="dosort(this)">Public';
    if (sort == -5) { tblHtml += ' ▼'; } 
    if (sort == 5) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 5%" data-field="wheel" onclick="dosort(this)">On Wheel';
    if (sort == -6) { tblHtml += ' ▼'; } 
    if (sort == 6) { tblHtml += ' ▲'; }
    tblHtml += '</th><th style="width: 35%"></th>';
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
        if(song.lastplayed) { lp = new Intl.DateTimeFormat('en').format(lpd); }
        tblHtml += '<td>' + lp + '</td>';
        tblHtml += '<td class="text-center"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" data-id="' + song.slid + '" ';
        if (song.public) { tblHtml += 'checked '; }
        tblHtml += 'onclick="togglepub(this)"/></div></td>';
        tblHtml += '<td class="text-center"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" data-id="' + song.slid + '" ';
        if (song.wheel) { tblHtml += 'checked '; }
        tblHtml += 'onclick="togglewheel(this)"/></div></td>';
        tblHtml += '<td><button style="margin: 2%;" class="btn btn-sm btn-danger" data-artist="' + song.artist + '" data-title="' + song.title + '" data-id="' + song.slid + '" onclick="deleteSong(this)">✖ Remove</button>';
        tblHtml += '<button style="margin: 2%;" class="btn btn-sm btn-primary" data-artist="' + song.artist + '" data-title="' + song.title + '" data-id="' + song.slid + '" onclick="queueSong(this)">📝 Queue</button>';
        tblHtml += '</td></tr>';
    }
    tblHtml += '<td colspan=7>';
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
    tblHtml += '<button onclick="addSong(this)">Add Song</button>';
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
    fixPageButtons();
}
function prevPage() {
    listOffset -= 10;
    if (listOffset < 0) { listOffset = 0; }
    writeSongList();
    fixPageButtons();
}
function nextPage() {
    listOffset += 10;
    if (listOffset > songlist.length) { listOffset = songlist.length - 10; }
    writeSongList();
    fixPageButtons();
}
function lastPage() {
    listOffset = songlist.length - 10;
    writeSongList();
    fixPageButtons();
}

function togglepub(e) {
    let pub = e.checked;
    let slid = e.getAttribute('data-id');
    const req = new XMLHttpRequest();
    req.onload = function () {
        loadList();
    };
    req.open('GET', APIURL + '/setsongpub/' + slid + '/' + (pub ? 1 : 0));
    req.send();
}

function togglewheel(e) {
    let wheel = e.checked;
    let slid = e.getAttribute('data-id');
    const req = new XMLHttpRequest();
    req.onload = function () {
        loadList();
    };
    req.open('GET', APIURL + '/setsongwheel/' + slid + '/' + (wheel ? 1 : 0));
    req.send();
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
                makeToast(SUCCESS, '❌ Success', title + ' has been removed from your list.');
                loadList();
            } else {
                makeToast(ERROR, '⚠️ Error', title + ' could not be removed from your list.');
            }
        }
    });
}

function queueSong(e) {
    let slid = e.getAttribute('data-id');
    let artist = e.getAttribute('data-artist');
    let title = e.getAttribute('data-title');
    const req = new XMLHttpRequest();
    req.onload = function () {
        if (this.responseText == 'OK') {
            makeToast(SUCCESS, '✔️ Success', title + ' by ' + artist + ' added to your queue');
        } else if (this.responseText == 'QF') {
            makeToast(SUCCESS, '✔️ Success', title + ' by ' + artist + ' added to your queue');
        } else if (this.responseText == 'NS') {
            makeToast(SUCCESS, '✔️ Success', title + ' by ' + artist + ' added to your queue');
        }
    };
    req.open('GET', APIURL + '/addreq/' + slid);
    req.send();
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
            if (this.responseText == 'QF') {
                makeToast(ERROR, '⚠️ Error', 'You already have a request in the queue for this user.');
            } else if (this.responseText == 'OK') {
                makeToast(SUCCESS, '✔️ Success', 'Your request for ' + title + ' by ' + artist + ' has been placed!');
            } else {
                makeToast(ERROR, '⚠️ Error', 'Something weird happened...');
            }
        }
    });
}

function addSong(e) {
    $('#addSongModal').modal('show');
}

function makeSongBoxesAutoComplete() {
    const treq = new XMLHttpRequest();
    treq.onload = function () {
        let titlelist = JSON.parse(this.responseText);
        let tlist = [];
        for (let i = 0; i < titlelist.length; i++) {
            tlist.push({label: titlelist[i].title, value: titlelist[i].title});
        }
        let titlebox = new Autocomplete(document.getElementById('addsongtitle'), {
            data: tlist,
            maximumItems: 10,
        });
    };
    treq.open('GET', APIURL + '/alltitles');
    treq.send();

    const areq = new XMLHttpRequest();
    areq.onload = function () {
        let artistlist = JSON.parse(this.responseText);
        let alist = [];
        for (let i = 0; i < artistlist.length; i++) {
            alist.push({label: artistlist[i].artist, value: artistlist[i].artist});
        }
        let artistbox = new Autocomplete(document.getElementById('addsongartist'), {
            data: alist,
            maximumItems: 10,
        });
    };
    areq.open('GET', APIURL + '/allartists');
    areq.send();
}
