var reqlist = []; // Holder for everything we get back
var listOffset = 0;
var shownames = false;

window.onload = function () {
    getShowNames();
    window.setInterval(getShowNames, 15000);
};

function getShowNames() {
    const reqr = new XMLHttpRequest();
    reqr.onload = function () {
        shownames = false;
        if (this.responseText == '1') {
            shownames = true;
        }
        loadReqList();
    };
    reqr.open('GET', APIURL + '/getshowreq');
    reqr.send();
}

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
    let len = 33;
    if (shownames) { len = 25; }
    let tblHtml = '<table class="table table-sm text-light fw-bold align-middle"><thead><tr>';
    if (shownames) {
        tblHtml += `<th style="width: ${len}%" data-field="artist">Requester</th>`;
    }
    tblHtml += `<th style="width: ${len}%" data-field="artist">Artist</th>`;
    tblHtml += `<th style="width: ${len}%" data-field="title">Title</th>`;
    tblHtml += `<th style="width: ${len}%" data-field="title">Time</th>`;
    tblHtml += '</tr></thead><tbody>';
    for (let i = listOffset; i < reqlist.length; i++) {
        let req = reqlist[i];
        let prioText = '';
        if (req.prio == -1) { prioText = 'text-secondary'; }
        if (req.prio == 1) { prioText = 'text-warning'; }
        tblHtml += `<tr class="${prioText}">`;
        if (shownames) {
            tblHtml += `<td>${req.rname}</td>`;
        }
        tblHtml += `<td>${req.artist}</td>`;
        tblHtml += `<td>${req.title}</td>`;
        let rd = Date.parse(req.timestamp);
        rds = new Intl.DateTimeFormat('en', { dateStyle: 'short', timeStyle: 'short' }).format(rd);
        tblHtml += `<td>${rds}</td></tr>`;
    }
    tblHtml += '</tbody></table>';
    document.getElementById('reqlist').innerHTML = tblHtml;
}


function removeReq(e) {
    let rid = e.getAttribute('data-rid');
    let title = e.getAttribute('data-title');
    const req = new XMLHttpRequest();
    req.onload = function () { 
        loadReqList();
    };
    req.open('GET', APIURL + '/removereq/' + rid);
    req.send();
}

function playReq(e) {
    let rid = e.getAttribute('data-rid');
    let slid = e.getAttribute('data-slid');
    const req = new XMLHttpRequest();
    req.onload = function () { 
        const rmreq = new XMLHttpRequest();
        rmreq.onload = function() {
            loadReqList();
        };
        rmreq.open('GET', APIURL + '/removereq/' + rid);
        rmreq.send();
    };
    req.open('GET', APIURL + '/play/' + slid);
    req.send();
}