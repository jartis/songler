var reqlist = []; // Holder for everything we get back
var listOffset = 0;

window.onload = function () {
    loadReqList();
    window.setInterval(loadReqList, 15000);
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
    let tblHtml = '<table class="table table-sm text-light fw-bold align-middle"><thead><tr>';
    tblHtml += '<th style="width: 21%" data-field="artist">Requester</th>';
    tblHtml += '<th style="width: 21%" data-field="artist">Artist</th>';
    tblHtml += '<th style="width: 21%" data-field="title">Title</th>';
    tblHtml += '<th style="width: 21%" data-field="title">Time</th>';
    tblHtml += '<th style="width: 16%"></th>';
    tblHtml += '</tr></thead><tbody>';
    for (let i = listOffset; i < reqlist.length; i++) {
        let req = reqlist[i];
        let prioText = '';
        if (req.prio == -1) { prioText = 'text-secondary'; }
        if (req.prio == 1) { prioText = 'text-warning'; }
        tblHtml += `<tr class="${prioText}">`;
        tblHtml += `<td>${req.rname}</td>`;
        tblHtml += `<td>${req.artist}</td>`;
        tblHtml += `<td>${req.title}</td>`;
        let rd = Date.parse(req.timestamp);
        rds = new Intl.DateTimeFormat('en', { dateStyle: 'short', timeStyle: 'short' }).format(rd);
        tblHtml += `<td>${rds}</td>`;
        tblHtml += '<td class="text-center">';
        tblHtml += `<button style="margin: 2%;" class="btn btn-sm btn-success" data-title="${req.title}" data-slid="${req.slid}" data-rid="${req.rid}" onclick="playReq(this)">✔️</button>`;
        tblHtml += `<button style="margin: 2%;" class="btn btn-sm btn-danger" data-title="${req.title}" data-slid="${req.slid}" data-rid="${req.rid}" onclick="removeReq(this)">✖</button>`;
        tblHtml += '</td></tr>';
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

function playReq() {
    let rid = e.getAttribute('data-rid');
    let slid = e.getAttribute('data-slid');
    let title = e.getAttribute('data-title');
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