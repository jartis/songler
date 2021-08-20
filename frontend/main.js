// Here's a crappy sample songlist while I test things out

// FOR DEBUGGING:
const APIURL = 'http://127.0.0.1:5000/api/v1';

const BLACK = '#000000';
const WHITE = '#FFFFFF';
const GREEN = '#008800';
const YELLOW = '#FFFF00';
const RED = '#FF0000';
const BLUE = '#0000FF';
const TRANSPARENT = '#00000000';

const USERID = 1; // I'm the video game boy! I'm the one who wins!

var maxPovertyQueueSize = 100;
var maxPriorityQueueSize = 100;
var maxTotalQueueSize = 100;

var wheelPalette = [
    '#3333FF',
    '#333333',
    '#FFFF33',
    '#33FF33',
    '#FF33FF',
    '#FF3333',
    '#33FFFF',
];
var wheelPaletteIndex = 0;

var songlist = [
    {
        'artist': 'artist',
        'title': 'title',
        'color': '#808080',
    }
];

var otherRandomSongs = [
];

var povertyQueue = [];
var priorityQueue = [];
var curWheelTitle = '';

// Set up a drawing target for the wheel
var wheelCanvas;
var wheelCtx;
var wheelBufCanvas;
var wheelBufCtx;
var wheelRotation = 0;
var wheelVelocity = 0;
var songIndex = 0;
var lastIndex = 0;
var wheelLeft = (1920 - 800) / 2;
var wheelTop = (1080 - 800) / 2;
var wheelSize = 800;

// Set up a drawing target for the request list
var queueCanvas;
var queueCtx;
var queueLeft = 150;
var queueTop = 20;
var queueSize = 800;

var REMOVE = 0; // Pull an option after it is selected, on a new spin
var xIndex = -1;

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
    let count = songlist.length;
    for (let i = 0; i < count; i++) {
        if (songlist[i].color == undefined) {
            songlist[i].color = wheelPalette[wheelPaletteIndex];
            wheelPaletteIndex++;
            if (Math.random() > 0.5) wheelPaletteIndex++;
            if (Math.random() > 0.5) wheelPaletteIndex++;
            wheelPaletteIndex %= wheelPalette.length;
        }
        wheelCtx.fillStyle = songlist[i].color;
        wheelCtx.lineStyle = BLACK;
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

function boundedRandomColor() {
    let r = Math.floor(Math.random() * 150) + 50;
    let g = Math.floor(Math.random() * 150) + 50;
    let b = Math.floor(Math.random() * 150) + 50;
    return '#' + r.toString(16) + g.toString(16) + b.toString(16);
}

function boundedBoldColor() {
    let color = '#';
    for (let i = 0; i < 6; i++) {
        if (Math.random() < 0.5) {
            color += "2";
        } else {
            color += "C";
        }
    }
    return color;
}

function drawLabel(context, textToFit, col) {
    context.font = '12px Arial';
    context.textAlign = 'right';
    context.textBaseline = 'middle';
    let l = getBrightness(col);
    if (l < 0.7) {
        drawShadowedText(context, 740, 400, textToFit, WHITE);
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

    drawWheel();
    drawAddSongToQueueButton();
    drawAddSongToWheelButton();
    drawAddPriorityButton();
    drawQueue();

    DrawScreen();
}

function drawWheel() {
    // Draw the wheel itself onto the buffer
    wheelBufCtx.translate(400, 400);
    wheelBufCtx.rotate(wheelRotation * (Math.PI / 180));
    wheelBufCtx.translate(-400, -400);
    wheelBufCtx.drawImage(wheelCanvas, 0, 0);
    wheelBufCtx.resetTransform();

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
    srcctx.drawImage(wheelBufCanvas, wheelLeft, wheelTop, wheelSize, wheelSize);
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
    queueCtx.font = '32px Arial';
    queueCtx.textAlign = 'left';
    queueCtx.textBaseline = 'top';

    drawShadowedText(queueCtx, 40, 0, "Request Queue:", WHITE);
    let lineY = 40;
    for (let i = 0; i < priorityQueue.length; i++) {
        drawShadowedText(queueCtx, 40, lineY, getFullName(priorityQueue[i]), YELLOW);
        lineY += 40;
    }
    for (let i = 0; i < povertyQueue.length; i++) {
        drawShadowedText(queueCtx, 40, lineY, getFullName(povertyQueue[i]), WHITE);
        lineY += 40;
    }

    if (xIndex >= 0) {
        drawShadowedText(queueCtx, 0, 40 + (40 * xIndex), '✖', RED);
    }

    srcctx.drawImage(queueCanvas, queueLeft, queueTop, queueSize, queueSize);
}

function drawAddSongToWheelButton() {
    // Draw an "Add Song" button
    srcctx.fillStyle = BLACK;
    srcctx.fillRect(1820, 980, 100, 100);
    srcctx.font = '16px Arial';
    srcctx.textAlign = 'center';
    srcctx.textBaseline = 'middle';
    srcctx.fillStyle = WHITE;
    drawBoldText(srcctx, 1870, 1000, 'ADD A', WHITE);
    drawBoldText(srcctx, 1870, 1020, 'RANDOM', WHITE);
    drawBoldText(srcctx, 1870, 1040, 'SONG TO', WHITE);
    drawBoldText(srcctx, 1870, 1060, 'THE WHEEL', WHITE);
}

function drawAddSongToQueueButton() {
    // Draw an "Add Song" button
    srcctx.fillStyle = BLUE;
    srcctx.fillRect(1620, 980, 100, 100);
    srcctx.font = '16px Arial';
    srcctx.textAlign = 'center';
    srcctx.textBaseline = 'middle';
    srcctx.fillStyle = WHITE;
    drawBoldText(srcctx, 1670, 1000, 'ADD A', WHITE);
    drawBoldText(srcctx, 1670, 1020, 'RANDOM', WHITE);
    drawBoldText(srcctx, 1670, 1040, 'SONG TO', WHITE);
    drawBoldText(srcctx, 1670, 1060, 'THE QUEUE', WHITE);
}

function drawAddPriorityButton() {
    // Draw an "Add Song" button
    srcctx.fillStyle = RED;
    srcctx.fillRect(1720, 980, 100, 100);
    srcctx.font = '16px Arial';
    srcctx.textAlign = 'center';
    srcctx.textBaseline = 'middle';
    srcctx.fillStyle = WHITE;
    drawBoldText(srcctx, 1770, 1000, 'ADD A', WHITE);
    drawBoldText(srcctx, 1770, 1020, 'PRIORITY', WHITE);
    drawBoldText(srcctx, 1770, 1040, 'SONG TO', WHITE);
    drawBoldText(srcctx, 1770, 1060, 'THE QUEUE', WHITE);
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
            if (!tryAddSongToQueue(songToAdd)) {
                songlist.push(songToAdd);
            }
        }
    }
    window.requestAnimationFrame(Update);
}

function getFullName(song) {
    return song.artist + ' - ' + song.title;
}

function tryAddSongToQueue(songToAdd, priority = false) {
    if (priority) {
        if (priorityQueue.length < maxPriorityQueueSize &&
            (priorityQueue.length + povertyQueue.length < maxTotalQueueSize)) {
            priorityQueue.push(songToAdd);
            return true;
        } else {
            return false;
        }
    } else {
        if (povertyQueue.length < maxPovertyQueueSize &&
            (priorityQueue.length + povertyQueue.length < maxTotalQueueSize)) {
            povertyQueue.push(songToAdd);
            return true;
        } else {
            return false;
        }
    }
}

function mouseMoved(e) {
    xIndex = -1;
    let mx = ((e.clientX - screenOffsetX) / (newWidth)) * 1920; // Relative position in overlay
    let my = ((e.clientY - screenOffsetY) / (newHeight)) * 1080; // Relative position in overlay
    let entrySize = queueSize / 20;
    if (mx > queueLeft && mx < queueLeft + queueSize && my > queueTop + entrySize && my < queueTop + queueSize) {
        let queueIndex = Math.floor((my - (queueTop + entrySize)) / (entrySize));
        let totalQueueSize = (priorityQueue.length) + (povertyQueue.length);
        if (queueIndex >= totalQueueSize) {
            return;
        }
        xIndex = queueIndex;
    }
}

function canvasClicked(e) {
    if (showControls) return; // Don't accidentally handle click events when you're diddling the display
    let mx = ((e.clientX - screenOffsetX) / (newWidth)) * 1920; // Relative position in overlay
    let my = ((e.clientY - screenOffsetY) / (newHeight)) * 1080; // Relative position in overlay
    if (mx > (wheelLeft + (wheelSize / 2) - (wheelSize / 16)) &&
        mx < (wheelLeft + (wheelSize / 2) + (wheelSize / 16)) &&
        my > (wheelTop + (wheelSize / 2) - (wheelSize / 16)) &&
        my < (wheelTop + (wheelSize / 2) + (wheelSize / 16))) {
        // Wheel spinny button
        if (wheelVelocity == 0 && songlist.length >= 1) {
            spinWheel();
        }
        return;
    }
    if (mx > 1820 && my > 980 && mx < 1920 && my < 1080) {
        // Add song button
        shuffle(otherRandomSongs);
        let songToAdd = otherRandomSongs.splice(0, 1)[0];
        addSong(songToAdd);
        return;
    }
    if (mx > 1720 && my > 980 && mx < 1820 && my < 1080) {
        // Add song button
        shuffle(otherRandomSongs);
        let songToAdd = otherRandomSongs.splice(0, 1)[0];
        if (!tryAddSongToQueue(songToAdd, true)) {
            otherRandomSongs.push(songToAdd);
        }
        return;
    }
    if (mx > 1620 && my > 980 && mx < 1720 && my < 1080) {
        // Add song button
        shuffle(otherRandomSongs);
        let songToAdd = otherRandomSongs.splice(0, 1)[0];
        if (!tryAddSongToQueue(songToAdd)) {
            otherRandomSongs.push(songToAdd);
        }
        return;
    }
    if (mx > queueLeft && mx < queueLeft + queueSize && my > queueTop && my < queueTop + queueSize) {
        // Remove a song from the queue
        let entrySize = queueSize / 20;
        let queueIndex = Math.floor((my - (queueTop + entrySize)) / (entrySize));
        let totalQueueSize = (priorityQueue.length) + (povertyQueue.length);
        if (queueIndex >= totalQueueSize) {
            return;
        }
        if (queueIndex < priorityQueue.length) {
            if (mx > (queueLeft + entrySize)) {
                if (playSong(priorityQueue[queueIndex])) {
                    console.log('Played priority song index ' + queueIndex);
                    priorityQueue.splice(queueIndex, 1);
                } else {
                    console.log("Error removing song from queue!");
                }
                mouseMoved(e); return;
            } else {
                console.log('Deleted priority song index ' + queueIndex);
                priorityQueue.splice(queueIndex, 1);
                mouseMoved(e); return;
            }
        }
        queueIndex -= priorityQueue.length;
        if (mx > (queueLeft + entrySize)) {
            if (playSong(povertyQueue[queueIndex])) {
                console.log('Played standard song index ' + queueIndex);
                povertyQueue.splice(queueIndex, 1);
            } else {
                console.log("Error removing song from queue!");
            }
            mouseMoved(e); return;
        } else {
            console.log('Deleted standard song index ' + queueIndex);
            povertyQueue.splice(queueIndex, 1);
            mouseMoved(e); return;
        }
    }
}

function playSong(song) {
    const req = new XMLHttpRequest();
    // req.onload = function () {
    //     return true;
    // };
    req.open('GET', APIURL + '/play?sid=' + song.songid, false);
    req.send();
    if (req.status == 200) {
        return true;
    }
    console.log('Error calling play() on song');
    return false;
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
    wheelSize = Number(e.target.value);
    if (wheelTop + wheelSize > 1080) {
        wheelTop = 1080 - wheelSize;
    }
    if (wheelLeft + wheelSize > 1920) {
        wheelLeft = 1920 - wheelSize;
    }
    document.getElementById('wheelTop').max = (1080 - wheelSize);
    document.getElementById('wheelLeft').max = (1920 - wheelSize);
}

function setWheelTop(e) {
    wheelTop = Number(e.target.value);
}

function setWheelLeft(e) {
    wheelLeft = Number(e.target.value);
}

function setQueueSize(e) {
    queueSize = Number(e.target.value);
}

function setQueueTop(e) {
    queueTop = Number(e.target.value);
}

function setQueueLeft(e) {
    queueLeft = Number(e.target.value);
}

// OnLoad initialization

window.onload = function () {
    initCanvases();
    window.addEventListener('resize', resize);
    listen('cbtn', 'click', showHideControls);
    window.addEventListener('click', canvasClicked);
    window.addEventListener('mousemove', mouseMoved);
    listen('wheelSize', 'input', setWheelSize);
    listen('wheelTop', 'input', setWheelTop);
    listen('wheelLeft', 'input', setWheelLeft);
    listen('queueSize', 'input', setQueueSize);
    listen('queueTop', 'input', setQueueTop);
    listen('queueLeft', 'input', setQueueLeft);
    initWheelCanvas();
    resize();
    Update();
    loadSongs();
};

function loadSongs() {
    const req = new XMLHttpRequest();
    req.onload = function () {
        let biglist = JSON.parse(this.responseText);
        shuffle(biglist);
        songlist = biglist.splice(0, 50);
        otherRandomSongs = biglist.splice(0, 50);
        shuffle(songlist);
        shuffle(otherRandomSongs);
        initWheelCanvas();
    };
    req.open('GET', APIURL + '/songlist?uid=' + USERID);
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

//#endregion Utils and Helpers