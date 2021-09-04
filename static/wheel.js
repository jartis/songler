// Here's a crappy sample songlist while I test things out

const BLACK = '#000000';
const WHITE = '#FFFFFF';
const GREEN = '#008800';
const YELLOW = '#FFFF00';
const RED = '#FF0000';
const BLUE = '#0000FF';
const BROWN = '#AA5500';
const TRANSPARENT = '#00000000';

// DEBUG
const LISTENING = false;
// DEBUG

// SAVEABLE config object!
var config = {};

var wheelPaletteIndex = 0;

var songlist = [
    {
        'artist': '',
        'title': 'LOADING',
        'color': '#808080',
    }
];

// Queue and associated display objs
var songQueue = [];

// Set up a drawing target for the wheel
var wheelCanvas;
var wheelCtx;
var wheelBufCanvas;
var wheelBufCtx;
var wheelRotation = 0;
var wheelVelocity = 0;
var songIndex = 0;
var lastIndex = 0;
var maxWheel = 50;
var wheelHighlight = -1;
var curWheelTitle = '';

// Set up a drawing target for the request list
var queueCanvas;
var queueCtx;

var songQueuePosIndex = -1;

// Tracking info for "session report"
var rpt_playedSongs = [];
var rpt_skippedSongs = [];
var rpt_startTime = Date.now();

// Noises!
var clicky = [
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
    new Audio('click.mp3'),
];
for (let i = 0; i < 10; i++) { clicky[i].volume = 0.2; }
var clickyIndex = 0;
var chime = new Audio('chime.mp3');
chime.volume = 0.2;

function addSong(songToAdd) {
    songlist.push(songToAdd);
    initWheelCanvas();
}

function initWheelCanvas() {
    //wheelRotation = 0;
    let count = songlist.length;
    for (let i = 0; i < count; i++) {
        if (songlist[i].color == undefined) {
            songlist[i].color = config.wheelPalette[wheelPaletteIndex];
            wheelPaletteIndex++;
            if (Math.random() > 0.5) wheelPaletteIndex++;
            if (Math.random() > 0.5) wheelPaletteIndex++;
            wheelPaletteIndex %= config.wheelPalette.length;
        }
        wheelCtx.fillStyle = songlist[i].color;
        wheelCtx.strokeStyle = BLACK;
        wheelCtx.lineWidth = 2;

        let slice = ((360 / count) * (Math.PI / 180));
        let angle = i * slice;
        wheelCtx.resetTransform();
        wheelCtx.translate(400, 400);
        wheelCtx.rotate(angle);
        wheelCtx.translate(-400, -400);
        wheelCtx.beginPath();
        wheelCtx.moveTo(400, 400);
        wheelCtx.lineTo(400 + (Math.cos(-slice / 2) * 350), 400 + (Math.sin(-slice / 2) * 350));
        wheelCtx.arc(400, 400, 350, -(slice / 2), slice / 2, false);
        wheelCtx.lineTo(400, 400);
        wheelCtx.fill();
        wheelCtx.stroke();
        // Draw song label
        let displayName = /*songlist[i][0] + ' - ' +*/ songlist[i].title;
        drawLabel(wheelCtx, displayName, songlist[i].color);
    }
}

function drawLabel(context, textToFit, col) {
    context.font = '12px Arial';
    context.textAlign = 'right';
    context.textBaseline = 'middle';
    let l = getBrightness(col);
    if (l < 0.5) {
        drawBoldText(context, 740, 400, textToFit, WHITE);
    } else {
        drawBoldText(context, 740, 400, textToFit, BLACK);
    }
}

function Draw() {
    // Clear the target
    srcctx.fillStyle = '#00880044'; // Partly transparent green for motion smooth/blur
    srcctx.fillRect(0, 0, 1920, 1080);
    // Clear the wheel buffer
    wheelBufCtx.fillStyle = TRANSPARENT;
    wheelBufCtx.clearRect(0, 0, 800, 800);

    if (config.wheelVisible) {
        drawWheel();
    }
    drawAddSongToQueueButton();
    if (config.queueVisible) {
        drawQueue();
    }

    DrawScreen();
}

function drawWheel() {
    // Draw the wheel itself onto the buffer
    wheelBufCtx.translate(400, 400);
    wheelBufCtx.rotate(wheelRotation * (Math.PI / 180));
    wheelBufCtx.translate(-400, -400);
    wheelBufCtx.drawImage(wheelCanvas, 0, 0);
    wheelBufCtx.resetTransform();

    // Draw the highlighted slice
    if (wheelHighlight > -1) {
        let slice = ((360 / songlist.length) * (Math.PI / 180));
        let angle = wheelHighlight * slice;
        wheelBufCtx.translate(400, 400);
        wheelBufCtx.rotate((wheelRotation * (Math.PI / 180)) + angle);
        wheelBufCtx.translate(-400, -400);

        wheelBufCtx.strokeStyle = WHITE;
        wheelBufCtx.fillStyle = '#FFFF80AA';
        wheelBufCtx.lineWidth = 8;
        wheelBufCtx.beginPath();
        wheelBufCtx.moveTo(400, 400);
        wheelBufCtx.lineTo(400 + (Math.cos(-slice / 2) * 350), 400 + (Math.sin(-slice / 2) * 350));
        wheelBufCtx.arc(400, 400, 350, -(slice / 2), slice / 2, false);
        wheelBufCtx.lineTo(400, 400);
        wheelBufCtx.fill();
        wheelBufCtx.stroke();

        wheelBufCtx.resetTransform();
    }

    // Draw the pointer
    wheelBufCtx.fillStyle = BLACK;
    wheelBufCtx.beginPath();
    wheelBufCtx.moveTo(745, 400);
    wheelBufCtx.lineTo(775, 390);
    wheelBufCtx.lineTo(775, 410);
    wheelBufCtx.lineTo(745, 400);
    wheelBufCtx.fill();

    // ...and the spin overlay
    wheelBufCtx.moveTo(400, 400);
    wheelBufCtx.beginPath();
    wheelBufCtx.arc(400, 400, 80, 0, 2 * Math.PI);
    wheelBufCtx.fill();

    // The spin text if necessary
    if (wheelVelocity == 0 && songlist.length >= 1) {
        drawClickToSpin();
    }

    // And the selected song
    wheelBufCtx.font = '32px Arial';
    wheelBufCtx.textAlign = 'center';
    wheelBufCtx.textBaseline = 'middle';
    wheelBufCtx.fillStyle = WHITE;
    drawShadowedText(wheelBufCtx, 400, 775, curWheelTitle, WHITE);

    // Then blurp it out to the src canvas
    srcctx.drawImage(wheelBufCanvas, config.wheelLeft, config.wheelTop, config.wheelSize, config.wheelSize);
}

function drawShadowedText(ctx, x, y, text, col, scol = BLACK) {
    ctx.fillStyle = scol;
    ctx.fillText(text, x + 1, y + 1);
    ctx.fillStyle = col;
    ctx.fillText(text, x, y);
}

function drawBoldText(ctx, x, y, text, col) {
    ctx.fillStyle = col;
    ctx.fillText(text, x, y);
    ctx.fillText(text, x + 1, y);
}

function drawQueue() {
    queueCtx.clearRect(0, 0, 800, 800);
    queueCtx.font = '16px Arial';
    queueCtx.textAlign = 'left';
    queueCtx.textBaseline = 'top';

    drawShadowedText(queueCtx, 20, 0, "Artist / Title", WHITE);
    drawShadowedText(queueCtx, 600, 0, "Requested by", WHITE);
    let lineY = 20;
    queueCtx.save();
    queueCtx.beginPath();
    queueCtx.rect(20, 0, 550, 800);
    queueCtx.clip();
    for (let i = 0; i < songQueue.length; i++) {
        let qCol = WHITE;
        if (songQueue[i].prio > 0) { qCol = YELLOW; }
        if (songQueue[i].prio < 0) { qCol = BROWN; }
        drawShadowedText(queueCtx, 20, lineY, getFullName(songQueue[i]), qCol);
        lineY += 20;
    }
    queueCtx.restore();
    lineY = 20;
    queueCtx.save();
    queueCtx.beginPath();
    queueCtx.rect(600, 0, 200, 800);
    queueCtx.clip();
    for (let i = 0; i < songQueue.length; i++) {
        let qCol = WHITE;
        if (songQueue[i].prio > 0) { qCol = YELLOW; }
        if (songQueue[i].prio < 0) { qCol = BROWN; }
        drawShadowedText(queueCtx, 600, lineY, songQueue[i].username, qCol);
        lineY += 20;
    }
    queueCtx.restore();

    if (songQueuePosIndex >= 0) {
        drawShadowedText(queueCtx, 0, 20 + (20 * songQueuePosIndex), '✖', RED);
    }

    srcctx.drawImage(queueCanvas, config.queueLeft, config.queueTop, config.queueSize, config.queueSize);
}

function drawClickToSpin() {
    wheelBufCtx.font = '24px Arial';
    wheelBufCtx.textAlign = 'center';
    wheelBufCtx.textBaseline = 'middle';
    wheelBufCtx.fillStyle = WHITE;
    drawBoldText(wheelBufCtx, 400, 370, 'CLICK', WHITE);
    drawBoldText(wheelBufCtx, 400, 400, 'TO', WHITE);
    drawBoldText(wheelBufCtx, 400, 430, 'SPIN', WHITE);
}

function spinWheel() {
    initWheelCanvas();
    wheelVelocity = 20 + (10 * Math.random());
}

function Update() {
    Draw();

    if (wheelVelocity > 0) {
        wheelRotation += wheelVelocity;
        wheelRotation %= 360;
        wheelVelocity *= 0.99;
        let sliceSize = (360 / songlist.length);
        songIndex = Math.floor((360 - wheelRotation + (sliceSize / 2)) / sliceSize);
        songIndex %= songlist.length;
        curWheelTitle = getFullName(songlist[songIndex]);
        if (lastIndex != songIndex) {
            clicky[clickyIndex].play();
            clickyIndex++;
            clickyIndex %= 10;
            lastIndex = songIndex;
        }

        if (wheelVelocity < 0.02) {
            wheelVelocity = 0;
            chime.play();
            let songToAdd = songlist.splice(songIndex, 1)[0];
            songToAdd.username = 'Random';
            if (!tryAddSongToQueue(songToAdd)) {
                songlist.push(songToAdd);
            }
            initWheelCanvas();
        }
    }
    window.requestAnimationFrame(Update);
}

function getFullName(song) {
    return song.artist + ' - ' + song.title;
}

function sortSongQueue() {
    songQueue.sort((a, b) => (a.timestamp < b.timestamp));
    songQueue.sort((a, b) => (a.prio > b.prio));
}

function tryAddSongToQueue(songToAdd, priority = 0) {
    if (songQueue.length >= maxTotalQueueSize) {
        return false;
    }
    songQueue.push(songToAdd);
    sortSongQueue();
    return true;
}

function distance(x1, y1, x2, y2) {
    let a = x1 - x2;
    let b = y1 - y2;
    let c = Math.sqrt(a * a + b * b);
    return Math.floor(c);
}

function mouseMoved(e) {
    songQueuePosIndex = -1;
    let mx = ((e.clientX - screenOffsetX) / (newWidth)) * 1920; // Relative position in overlay
    let my = ((e.clientY - screenOffsetY) / (newHeight)) * 1080; // Relative position in overlay

    // Check for wheel overlap first
    if (config.wheelVisible) {
        if (wheelVelocity == 0) {
            wheelHighlight = -1;
            if (mx > config.wheelLeft && mx < config.wheelLeft + config.wheelSize &&
                my > config.wheelTop && my < config.wheelTop + config.wheelSize) {
                let wheelCenterX = config.wheelLeft + (config.wheelSize / 2);
                let wheelCenterY = config.wheelTop + (config.wheelSize / 2);
                let d = distance(mx, my, wheelCenterX, wheelCenterY);
                if (d < (config.wheelSize * 7 / 16) && d > (config.wheelSize / 10)) {
                    let posAngle = Math.atan2(wheelCenterY - my, wheelCenterX - mx) * 180 / Math.PI;
                    posAngle -= wheelRotation;
                    while (posAngle < 0) { posAngle += 360; }
                    posAngle %= 360;

                    let sliceSize = (360 / songlist.length);
                    wheelHighlight = Math.floor((180 + posAngle + (sliceSize / 2)) / sliceSize);
                    wheelHighlight %= songlist.length;
                }
                else { wheelHighlight = -1; }
            }
        }
    }

    if (config.queueVisible) {
        let entrySize = config.queueSize / 40;
        if (mx > config.queueLeft && mx < config.queueLeft + config.queueSize &&
            my > config.queueTop + entrySize && my < config.queueTop + config.queueSize) {
            let queueIndex = Math.floor((my - (config.queueTop + entrySize)) / (entrySize));
            if (queueIndex >= songQueue.length) {
                return;
            }
            songQueuePosIndex = queueIndex;
        }
    }
}

function canvasClicked(e) {
    // Taking this out for now. Lock in "config mode" to ignore canvas clicks?
    // if (showControls) return; // Don't accidentally handle click events when you're diddling the display

    let mx = ((e.clientX - screenOffsetX) / (newWidth)) * 1920; // Relative position in overlay
    let my = ((e.clientY - screenOffsetY) / (newHeight)) * 1080; // Relative position in overlay

    // Wheel events:
    if (config.wheelVisible) {
        // Wheel spin button
        if (mx > (config.wheelLeft + (config.wheelSize / 2) - (config.wheelSize / 16)) &&
            mx < (config.wheelLeft + (config.wheelSize / 2) + (config.wheelSize / 16)) &&
            my > (config.wheelTop + (config.wheelSize / 2) - (config.wheelSize / 16)) &&
            my < (config.wheelTop + (config.wheelSize / 2) + (config.wheelSize / 16))) {
            // Wheel spinny button
            if (wheelVelocity == 0 && songlist.length >= 1) {
                spinWheel();
            }
            return;
        }
        // BEFORE the request list, check if there's a wheel song highlighted, if there is kill it
        // But only when the wheel isn't spinning!
        if (wheelHighlight > -1 && wheelVelocity == 0) {
            rpt_skippedSongs.push(songlist[wheelHighlight].slid);
            songlist.splice(wheelHighlight, 1);
            initWheelCanvas();
            return;
        }
    }

    // Arbitrary "Debug" Button
    if (mx > 1620 && my > 980 && mx < 1720 && my < 1080) {
        // Check Requests button
        getRequests();
        return;
    }

    if (config.queueVisible) {
        if (mx > config.queueLeft && mx < config.queueLeft + config.queueSize &&
            my > config.queueTop && my < config.queueTop + config.queueSize) {
            // Remove a song from the queue
            let entrySize = config.queueSize / 40;
            let queueIndex = Math.floor((my - (config.queueTop + entrySize)) / (entrySize));
            if (queueIndex >= songQueue.length) {
                return;
            }
            if (mx > (config.queueLeft + entrySize)) {
                if (playSong(songQueue[queueIndex])) {
                    console.log('Played song index ' + queueIndex);
                    songQueue.splice(queueIndex, 1);
                } else {
                    console.log("Error removing song from queue!");
                }
                mouseMoved(e); return;
            } else {
                console.log('Deleted song index ' + queueIndex);
                rpt_skippedSongs.push(songQueue[queueIndex].slid);
                songQueue.splice(queueIndex, 1);
                removeRequest(songQueue[queueIndex].rid);
                mouseMoved(e); return;
            }
        }
    }
}

function playSong(song) {
    rpt_playedSongs.push(song.slid);
    const req = new XMLHttpRequest();
    // req.onload = function () {
    //     return true;
    // };
    req.open('GET', APIURL + '/play/' + song.slid, false);
    req.send();
    if (req.status == 200) {
        if (song.rid) {
            removeRequest(song.rid);
        }
        return true;
    }
    const rreq = new XMLHttpRequest();

    console.log('Error storing song play in DB');
    return false;
}

function removeRequest(rid) {
    const req = new XMLHttpRequest();
    req.onload = function () { };
    req.open('GET', APIURL + '/removereq/' + rid);
    req.send();
}

function getRequests() {
    if (config.dopoll == false) {
        return;
    }
    const req = new XMLHttpRequest();
    req.onload = function () {
        let reqs = JSON.parse(this.responseText);
        for (let i = 0; i < reqs.length; i++) {
            let song = reqs[i];
            if (song.rname == null) {
                song.rname = 'Anonymous';
            }
            tryAddSongToQueue(song);
        }
        sortSongQueue();
    };
    req.open('GET', APIURL + '/getreqs');
    req.send();
}

//#region Utils and Helpers

function resize() {
    dstCanvas.width = window.innerWidth;
    dstCanvas.height = window.innerHeight;

    if (dstCanvas.width / dstCanvas.height > dscale) {
        newHeight = dstCanvas.height;
        newWidth = newHeight / 9 * 16;
        dScale = newHeight / 1080;
    } else {
        newWidth = dstCanvas.width;
        newHeight = newWidth / 16 * 9;
        dScale = newWidth / 1920;
    }

    screenOffsetX = Math.abs((dstCanvas.width - newWidth)) / 2;
    screenOffsetY = Math.abs((dstCanvas.height - newHeight)) / 2;

    DrawScreen();
}

function DrawScreen() {
    // Maybe this should live elsewhere but
    dstctx.fillStyle = GREEN;
    dstctx.fillRect(0, 0, dstCanvas.width, dstCanvas.height);
    dstctx.drawImage(srcctx.canvas, 0, 0, 1920, 1080, screenOffsetX, screenOffsetY, newWidth, newHeight);
}

function setWheelSize(e) {
    config.wheelSize = Number(e.target.value);
    if (config.wheelTop + config.wheelSize > 1080) {
        config.wheelTop = 1080 - config.wheelSize;
    }
    if (config.wheelLeft + config.wheelSize > 1920) {
        config.wheelLeft = 1920 - config.wheelSize;
    }
    document.getElementById('wheelTop').max = (1080 - config.wheelSize);
    document.getElementById('wheelLeft').max = (1920 - config.wheelSize);
}

function setWheelTop(e) {
    config.wheelTop = Number(e.target.value);
}

function setWheelLeft(e) {
    config.wheelLeft = Number(e.target.value);
}

function setQueueSize(e) {
    config.queueSize = Number(e.target.value);
}

function setQueueTop(e) {
    config.queueTop = Number(e.target.value);
}

function setQueueLeft(e) {
    config.queueLeft = Number(e.target.value);
}

function toggleWheelVis(e) {
    config.wheelVisible = !config.wheelVisible;
    document.getElementById('wheelVis').checked = config.wheelVisible;
}

function toggleQueueVis(e) {
    config.queueVisible = !config.queueVisible;
    document.getElementById('queueVis').checked = config.queueVisible;
}

function setPoll(e) {
    config.dopoll = document.getElementById('doPoll').checked;
}

function refillWheel(e) {
    let songsToGet = maxWheel - songlist.length;
    let curList = [];
    for (let i = 0; i < songlist.length; i++) {
        curList.push(Number(songlist[i].slid));
    }
    for (let i = 0; i < rpt_playedSongs.length; i++) {
        curList.push(Number(rpt_playedSongs[i]));
    }
    for (let i = 0; i < rpt_skippedSongs.length; i++) {
        curList.push(Number(rpt_skippedSongs[i]));
    }

    const req = new XMLHttpRequest();
    req.onload = function () {
        let list = JSON.parse(this.responseText);
        for(let i = 0; i < list.length; i++) {
            list[i].prio = -1;
        }
        songlist.push.apply(songlist, list);
        initWheelCanvas();
    };
    req.open('GET', APIURL + '/more?uid=' + uid + '&count=' + songsToGet + '&list=' + curList);
    req.send();
}

function handleKeys(e) {
    switch (e.code) {
        case 'KeyW':
            toggleWheelVis();
            break;
        case 'KeyR':
            toggleQueueVis();
            break;
        case 'KeyC':
            showHideControls();
            break;
        default:
            break;
    }
}

// OnLoad initialization

window.onload = function () {
    initCanvases();
    initWheelCanvas();
    resize();
    Update();
    getConfig();
    loadSongs();

    window.addEventListener('resize', resize);
    window.addEventListener('click', canvasClicked);
    window.addEventListener('mousemove', mouseMoved);
    window.addEventListener('keydown', handleKeys);
    window.addEventListener('beforeunload', saveConfig);
    window.setInterval(getRequests, 15000);
    listen('cbtn', 'click', showHideControls);
    listen('wheelSize', 'input', setWheelSize);
    listen('wheelTop', 'input', setWheelTop);
    listen('wheelLeft', 'input', setWheelLeft);
    listen('queueSize', 'input', setQueueSize);
    listen('queueTop', 'input', setQueueTop);
    listen('queueLeft', 'input', setQueueLeft);
    listen('wheelRefill', 'click', refillWheel);
    listen('wheelVis', 'input', toggleWheelVis);
    listen('doPoll', 'input', setPoll);
};

function getConfig() {
    const req = new XMLHttpRequest();
    req.onload = function () {
        if (this.responseText == '0') {
            makeDefaultConfig();
            saveConfig();
        } else {
            let cfgRow = JSON.parse(this.responseText);
            config = JSON.parse(cfgRow.config);
        }
    };
    req.open('GET', APIURL + '/getconfig');
    req.send();
}

function saveConfig() {
    data = {
        config: JSON.stringify(config),
    };

    $.ajax({
        type: 'POST',
        url: APIURL + '/saveconfig',
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        complete: function (msg) {
            if (msg.status == 200) {
                // woo
            } else {
                // OH CRAP EVERYTHING IS ON FIRE
            }
        }
    });
}

function loadSongs() {
    const req = new XMLHttpRequest();
    req.onload = function () {
        let biglist = JSON.parse(this.responseText);
        biglist = biglist.splice(0, maxWheel * 2);
        shuffle(biglist);
        for (let i = 0; i < biglist.length; i++) {
            biglist[i].prio = -1;
        }
        songlist = biglist.splice(0, maxWheel);
        shuffle(songlist);
        initWheelCanvas();
    };
    req.open('GET', APIURL + '/allsongs/' + uid);
    req.send();
}

// Canvases
var srcCanvas;
var srcctx;
var dstCanvas;
var dstctx;

// Scaling
var dscale = 1920 / 1080;
var screenOffsetX = 0;
var screenOffsetY = 0;
var newWidth = 0;
var newHeight = 0;

// Util functions
function listen(id, evt, fnc) {
    document.getElementById(id).addEventListener(evt, fnc, false);
}

var showControls = true;

function showHideControls(e) {
    showControls = !showControls;
    if (!showControls) {
        document.getElementById('cpan').style.display = 'none';
        document.getElementById('clbl').innerText = '»';
    } else {
        document.getElementById('cpan').style.display = 'inline-block';
        document.getElementById('clbl').innerText = '«';
    }
}

function initCanvases() {
    srcCanvas = document.createElement('canvas');
    srcCanvas.width = 1920;
    srcCanvas.height = 1080;
    srcctx = srcCanvas.getContext('2d');
    srcctx.fillStyle = GREEN;
    srcctx.fillRect(0, 0, 1920, 1080);

    dstCanvas = document.getElementById('canvas');
    dstCanvas.width = window.innerWidth;
    dstCanvas.height = window.innerHeight;
    dstctx = dstCanvas.getContext('2d');
    dstctx.fillStyle = GREEN;
    dstctx.fillRect(0, 0, dstCanvas.width, dstCanvas.height);

    wheelCanvas = document.createElement('canvas');
    wheelCanvas.width = 800;
    wheelCanvas.height = 800;
    wheelCtx = wheelCanvas.getContext('2d');
    wheelCtx.fillStyle = TRANSPARENT;
    wheelCtx.fillRect(0, 0, 800, 800);

    wheelBufCanvas = document.createElement('canvas');
    wheelBufCanvas.width = 800;
    wheelBufCanvas.height = 800;
    wheelBufCtx = wheelBufCanvas.getContext('2d');
    wheelBufCtx.fillStyle = TRANSPARENT;
    wheelBufCtx.fillRect(0, 0, 800, 800);

    queueCanvas = document.createElement('canvas');
    queueCanvas.width = 800;
    queueCanvas.height = 800;
    queueCtx = queueCanvas.getContext('2d');
    queueCtx.fillStyle = TRANSPARENT;
    queueCtx.fillRect(0, 0, 800, 800);
}

function shuffle(array) {
    var currentIndex = array.length, randomIndex;

    // While there remain elements to shuffle...
    while (currentIndex != 0) {

        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex--;

        // And swap it with the current element.
        [array[currentIndex], array[randomIndex]] = [
            array[randomIndex], array[currentIndex]];
    }

    return array;
}

function getBrightness(rgbstr) {
    rgbstr = rgbstr.replace(/^\s*#|\s*$/g, '');
    if (rgbstr.length == 3) {
        rgbstr = rgbstr.replace(/(.)/g, '$1$1');
    }
    let r = parseInt(rgbstr.substr(0, 2), 16) / 255;
    let g = parseInt(rgbstr.substr(2, 2), 16) / 255;
    let b = parseInt(rgbstr.substr(4, 2), 16) / 255;
    let l = (0.2126 * r + 0.7152 * g + 0.0722 * b);
    return l;
}

function updateConfig() {
    if (config.version == 1) {
        config.version = 2;
        config.dopoll = true;
    }
}

function makeDefaultConfig() {
    config = {
        version: 2,

        maxPovertyQueueSize: 100,
        maxPriorityQueueSize: 100,
        maxTotalQueueSize: 100,

        wheelLeft: (1920 - 800) / 2,
        wheelTop: (1080 - 800) / 2,
        wheelSize: 800,
        wheelVisible: true,

        queueLeft: 150,
        queueTop: 20,
        queueSize: 800,
        queueVisible: true,

        wheelPalette: [
            '#3333FF',
            '#333333',
            '#FFFF33',
            '#33FF33',
            '#FF33FF',
            '#FF3333',
            '#33FFFF',
        ],

        dopoll: false,
    };
}

//#endregion Utils and Helpers