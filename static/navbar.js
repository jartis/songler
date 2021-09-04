window.addEventListener('load', populateSearch);
var optlist = [];

function populateSearch() {
    // Add the users
    const req = new XMLHttpRequest();
    req.onload = function () {
        let rawlist = JSON.parse(this.responseText);
        for (let i = 0; i < rawlist.length; i++) {
            let entry = {
                label: 'User Profile: ' + rawlist[i].displayname,
                value: '/profile/' + rawlist[i].displayname,
            };
            optlist.push(entry);
            entry = {
                label: rawlist[i].displayname + '\'s Public Songlist',
                value: '/songlist/' + rawlist[i].displayname,
            };
            optlist.push(entry);
        }
    };
    req.open('GET', APIURL + '/allusers');
    req.send();
    // Add the songs
    const areq = new XMLHttpRequest();
    areq.onload = function() {
        let rawlist = JSON.parse(this.responseText);
        for (let i = 0; i < rawlist.length; i++) {
            let entry = {
                label: 'Artist: ' + rawlist[i].artist,
                value: '/artist/' + rawlist[i].aid,
            };
            optlist.push(entry);
        }
    };
    areq.open('GET', APIURL + '/allartists');
    areq.send();

    const sreq = new XMLHttpRequest();
    sreq.onload = function () {
        let rawlist = JSON.parse(this.responseText);
        for (let i = 0; i < rawlist.length; i++) {
            let entry = {
                label: 'Song: ' + rawlist[i].title + ' by ' + rawlist[i].artist,
                value: '/song/' + rawlist[i].sid,
            };
            optlist.push(entry);
        }
    };
    sreq.open('GET', APIURL + '/allsongs');
    sreq.send();
}

let srch = new Autocomplete(document.getElementById('srch'), {
    data: optlist,
    onSelectItem: ({ label, value }) => {
        window.location.href = value;
    },
    maximumItems: 10,
});

function updateReqBadge() {
    const breq = new XMLHttpRequest();
    breq.onload = function () {
        if (isNaN(Number(this.responseText))){
            document.getElementById('reqbadge').innerText = '?';
        } else {
            document.getElementById('reqbadge').innerText = this.responseText;
        }
    };
    breq.open('GET', APIURL + '/reqcount');
    breq.send();
}
