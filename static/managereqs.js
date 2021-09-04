var reqlist = []; // Holder for everything we get back
var listOffset = 0;

window.onload = function () {
    loadReqList();
};

function loadReqList() {
    const reqr = new XMLHttpRequest();
    reqr.onload = function () {
        reqlist = JSON.parse(this.responseText);
        writeReqList();
    };
    reqr.open('GET', APIURL + '/getreqs');
    reqr.send();
}

// Fields: rid, slid, rname, artist, title, prio, timestamp
// Defaults to sorted by priority first, then timestamp, oldest to newest


function writeReqList() {
    let tblHtml = 'No requests in your queue!';
    if (reqlist.length > 0) {
        tblHtml = '<table class="table table-bordered table-secondary table-hover align-middle table-striped"><thead><tr>';
        tblHtml += '<th style="width: 18%" class="text-center" data-field="artist">Requester</th>';
        tblHtml += '<th style="width: 18%" class="text-center" data-field="artist">Artist</th>';
        tblHtml += '<th style="width: 18%" class="text-center" data-field="title">Title</th>';
        tblHtml += '<th style="width: 18%" class="text-center" data-field="title">Time</th>';
        tblHtml += '<th style="width: 28%"></th>';
        tblHtml += '</tr></thead><tbody>';
        let maxLength = Math.min(reqlist.length, listOffset + 10);
        let curPage = Math.ceil(listOffset / 10) + 1;
        let lastPage = Math.ceil(reqlist.length / 10);
        for (let i = listOffset; i < maxLength; i++) {
            let req = reqlist[i];
            let prioname = '';
            if (req.prio == -1) { prioname = 'table-secondary'; }
            if (req.prio == 1) { prioname = 'table-warning'; }
            tblHtml += `<tr class="${prioname}">`;
            tblHtml += `<td>${req.rname}</td>`;
            tblHtml += `<td>${req.artist}</td>`;
            tblHtml += `<td>${req.title}</td>`;
            let rd = Date.parse(req.timestamp);
            rds = new Intl.DateTimeFormat('en', { dateStyle: 'short', timeStyle: 'short' }).format(rd);
            tblHtml += `<td>${rds}</td>`;
            tblHtml += '<td class="text-center">';
            tblHtml += `<button style="margin: 2%;" class="btn btn-sm btn-success" data-title="${req.title}" data-slid="${req.slid}" data-rid="${req.rid}" onclick="playReq(this)">▶️ Mark as Played</button>`;
            tblHtml += `<button style="margin: 2%;" class="btn btn-sm btn-danger" data-title="${req.title}" data-slid="${req.slid}" data-rid="${req.rid}" onclick="removeReq(this)">✖ Remove</button>`;
            tblHtml += '</td></tr>';
        }
        tblHtml += '<td colspan=5 class="text-center">';
        tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
        tblHtml += '<button id="fp" type="button" onclick="firstPage();" class="btn btn-secondary">« First Page</button>';
        tblHtml += '</span>';
        tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
        tblHtml += '<button id="pp" type="button" onclick="prevPage();" class="btn btn-secondary">‹ Prev Page</button>';
        tblHtml += '</span>';
        tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
        tblHtml += `<span>${curPage.toString()} / ${lastPage.toString()}</span>`;
        tblHtml += '</span>';
        tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
        tblHtml += '<button id="np" type="button" onclick="nextPage();" class="btn btn-secondary">Next Page ›</button>';
        tblHtml += '</span>';
        tblHtml += '<span style="width: 20%; margin: auto; padding:2%;">';
        tblHtml += '<button id="lp" type="button" onclick="lastPage();" class="btn btn-secondary">Last Page »</button></td>';
        tblHtml += '</span>';
        tblHtml += '</tbody></table>';
    }
    document.getElementById('reqlist').innerHTML = tblHtml;
}

function fixPageButtons() {
    $("fp").hide();
    $("pp").hide();
    $("np").hide();
    $("lp").hide();
    if (listOffset > 0) { $("fp").show(); $("pp").show(); }
    if (listOffset < reqlist.length - 10) { $("np").show(); $("lp").show(); }
}
function firstPage() {
    listOffset = 0;
    writeReqList();
    fixPageButtons();
}
function prevPage() {
    listOffset -= 10;
    if (listOffset < 0) { listOffset = 0; }
    writeReqList();
    fixPageButtons();
}
function nextPage() {
    listOffset += 10;
    if (listOffset > reqlist.length) {
        listOffset = reqlist.length - 10;
        if (listOffset < 0) {
            listOffset = 0;
        }
    }
    writeReqList();
    fixPageButtons();
}
function lastPage() {
    listOffset = reqlist.length - 10;
    if (listOffset < 0) {
        listOffset = 0;
    }
    writeReqList();
    fixPageButtons();
}

function removeReq(e) {
    let rid = e.getAttribute('data-rid');
    let title = e.getAttribute('data-title');
    const req = new XMLHttpRequest();
    req.onload = function () {
        makeToast(SUCCESS, '❌ Success', title + ' has been removed from your queue.');
        loadReqList();
        updateReqBadge();
    };
    req.open('GET', APIURL + '/removereq/' + rid);
    req.send();
}

function playReq() {
    let rid = e.getAttribute('data-rid');
    let slid = e.getAttribute('data-slid');
    let title = e.getAttribute('data-title');
    const req = new XMLHttpRequest();
    req.onload = function () {
        const rmreq = new XMLHttpRequest();
        rmreq.onload = function () {
            makeToast(SUCCESS, '✔️ Success', title + ' has been marked as played.');
            loadReqList();
            updateReqBadge();
        };
        rmreq.open('GET', APIURL + '/removereq/' + rid);
        rmreq.send();
    };
    req.open('GET', APIURL + '/play/' + slid);
    req.send();
}