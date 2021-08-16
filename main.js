// Here's a crappy sample songlist while I test things out

const BLACK = '#000000';
const WHITE = '#FFFFFF';
const GREEN = '#00FF00';
const YELLOW = '#FFFF00';
const RED = '#FF0000';
const BLUE = '#0000FF';

var maxPovertyQueueSize = 10;
var maxPriorityQueueSize = 10;
var maxTotalQueueSize = 5;

var songlist = [
    ["The Beatles", "Blackbird"],
    ["Green Day", "Basket Case"],
    ["Dr. Hook", "The Wonderful Soup Stone"],
    ["Stan Rogers", "The Mary Ellen Carter"],
];

var otherRandomSongs = [
    ["The Eagles", "Certain Kind Of Fool"],
    ["Jimi Hendrix", "Bold As Love"],
    ["Tesla", "Love Song"],
    ["Everclear", "Fire Maple Song"],
    ["Aerosmith", "Dream On"],
    ["Beach Boys", "Surfer Girl"],
    ["The Who", "5:15"],
    ["Dire Straits", "Sultans of Swing"],
    ["The Lumineers", "Cleopatra"],
    ["Glen Campbell", "Wichita Lineman"],
    ["Jim Croce", "Operator"],
    ["Weezer", "Longtime Sunshine"],
    ["The Beatles", "Two Of Us"],
    ["Katamari Damacy", "Lonely Rolling Star"],
    ["Nickelback", "How You Remind Me"],
    ["The Flaming Lips", "The Castle"],
    ["Alice In Chains", "Got Me Wrong"],
    ["Pink Floyd", "Mother"],
    ["Stone Temple Pilots", "Still Remains"],
];

var povertyQueue = [];
var priorityQueue = [];

// Set up a drawing target for the wheel
var wheelCanvas;
var wheelCtx;
var wheelRotation = 0;
var wheelVelocity = 0;
var songIndex = 0;
var REMOVE = 0; // Pull an option after it is selected, on a new spin

function addSong(songToAdd) {
    songlist.push(songToAdd);
    initWheelCanvas();
}

function initWheelCanvas() {
    wheelCanvas = document.createElement('canvas');
    wheelCanvas.width = 800;
    wheelCanvas.height = 800;
    wheelCtx = wheelCanvas.getContext('2d');
    wheelCtx.fillStyle = '#00000000'; // Transparent
    wheelCtx.fillRect(0, 0, 800, 800);

    let count = songlist.length;
    for (let i = 0; i < count; i++) {
        if (songlist[i].length < 3) {
            songlist[i][2] = boundedRandomColor(); // Pick a color for this song!
        }
        wheelCtx.fillStyle = songlist[i][2];

        let slice = ((360 / count) * (Math.PI / 180));
        let angle = i * slice;
        wheelCtx.resetTransform();
        wheelCtx.translate(400, 400);
        wheelCtx.rotate(angle);
        wheelCtx.translate(-400, -400);
        wheelCtx.beginPath();
        wheelCtx.arc(400, 400, 350, -(slice / 2), slice / 2, false);
        wheelCtx.lineTo(400, 400);
        wheelCtx.fill();
        // Draw song label
        let displayName = songlist[i][0] + ' - ' + songlist[i][1];
        fitText(wheelCtx, displayName, 250);
    }
}

function boundedRandomColor() {
    let r = Math.floor(Math.random() * 150) + 50;
    let g = Math.floor(Math.random() * 150) + 50;
    let b = Math.floor(Math.random() * 150) + 50;
    return '#' + r.toString(16) + g.toString(16) + b.toString(16);
}

function fitText(context, textToFit, maxWidth) {
    context.font = '12px Arial';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    drawShadowedText(context, 600, 400, textToFit, WHITE);
}

function Draw() {
    // Clear the target
    srcctx.fillStyle = GREEN;
    srcctx.fillRect(0, 0, 1920, 1080);

    // Draw the wheel itself
    srcctx.translate(960, 540);
    srcctx.rotate(wheelRotation * (Math.PI / 180));
    srcctx.translate(-960, -540);
    srcctx.drawImage(wheelCanvas, 560, 140);
    srcctx.resetTransform();

    // Draw the pointer and the spin overlay
    srcctx.fillStyle = BLACK;
    srcctx.beginPath();
    srcctx.translate((1920 - 800) / 2, (1080 - 800) / 2);
    srcctx.moveTo(745, 400);
    srcctx.lineTo(775, 390);
    srcctx.lineTo(775, 410);
    srcctx.lineTo(745, 400);
    srcctx.fill();
    srcctx.resetTransform();
    srcctx.moveTo(400, 400);
    srcctx.beginPath();
    srcctx.arc(960, 540, 45, 0, 2 * Math.PI);
    srcctx.fill();
    if (wheelVelocity == 0 && songlist.length >= 1) {
        drawWheel();
    }
    drawAddSongToQueueButton();
    drawAddSongToWheelButton();
    drawAddPriorityButton();
    drawQueue();

    DrawScreen();
}

function drawShadowedText(ctx, x, y, text, col) {
    ctx.fillStyle = BLACK;
    ctx.fillText(text, x + 1, y + 1);
    ctx.fillStyle = col;
    ctx.fillText(text, x - 1, y - 1);
}

function drawBoldText(ctx, x, y, text, col) {
    ctx.fillStyle = col;
    ctx.fillText(text, x, y);
    ctx.fillText(text, x + 1, y);
}

function drawQueue() {
    srcctx.font = '24px Arial';
    srcctx.textAlign = 'left';
    srcctx.textBaseline = 'middle';

    drawShadowedText(srcctx, 180, 40, "Request Queue:", WHITE);
    srcctx.textBaseline = 'top';
    let lineY = 80;
    for (let i = 0; i < priorityQueue.length; i++) {
        drawShadowedText(srcctx, 180, lineY, priorityQueue[i][0] + ' - ' + priorityQueue[i][1], YELLOW);
        lineY += 30;
    }
    for (let i = 0; i < povertyQueue.length; i++) {
        drawShadowedText(srcctx, 180, lineY, povertyQueue[i][0] + ' - ' + povertyQueue[i][1], WHITE);
        lineY += 30;
    }
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

function drawWheel() {
    srcctx.font = '16px Arial';
    srcctx.textAlign = 'center';
    srcctx.textBaseline = 'middle';
    srcctx.fillStyle = WHITE;
    drawBoldText(srcctx, 960, 520, 'CLICK', WHITE);
    drawBoldText(srcctx, 960, 540, 'TO', WHITE);
    drawBoldText(srcctx, 960, 560, 'SPIN', WHITE);
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
        if (wheelVelocity < 0.02) {
            wheelVelocity = 0;
            let sliceSize = (360 / songlist.length);
            songIndex = Math.floor((360 - wheelRotation + (sliceSize / 2)) / sliceSize);
            songIndex %= songlist.length;
            tryAddSongToQueue((songlist.splice(songIndex, 1)[0]));

        }
    }
    window.requestAnimationFrame(Update);
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

function canvasClicked(e) {
    let mx = ((e.clientX - screenOffsetX) / (newWidth)) * 1920;
    let my = ((e.clientY - screenOffsetY) / (newHeight)) * 1080;
    if (mx > (960 - 45) && mx < (960 + 45) && my > (540 - 45) && my < (540 + 45)) {
        // Wheel spinny button
        if (wheelVelocity == 0 && songlist.length >= 1) {
            spinWheel();
        }
    } else if (mx > 1820 && my > 980 && mx < 1920 && my < 1080) {
        // Add song button
        shuffle(otherRandomSongs);
        let songToAdd = otherRandomSongs.splice(0, 1)[0];
        addSong(songToAdd);
    } else if (mx > 1720 && my > 980 && mx < 1820 && my < 1080) {
        // Add song button
        shuffle(otherRandomSongs);
        let songToAdd = otherRandomSongs.splice(0, 1)[0];
        if (!tryAddSongToQueue(songToAdd, true)) {
            otherRandomSongs.push(songToAdd);
        }
    } else if (mx > 1620 && my > 980 && mx < 1720 && my < 1080) {
        // Add song button
        shuffle(otherRandomSongs);
        let songToAdd = otherRandomSongs.splice(0, 1)[0];
        if (!tryAddSongToQueue(songToAdd)) {
            otherRandomSongs.push(songToAdd);
        }
    } else if (mx > 180 && mx < 580 && my > 80) {
        // Remove a song from the queue
        let queueIndex = Math.floor((my - 80) / 30);
        let totalQueueSize = (priorityQueue.length) + (povertyQueue.length);
        if (queueIndex >= totalQueueSize) {
            return;
        }
        if (queueIndex < priorityQueue.length) {
            priorityQueue.splice(queueIndex, 1);
            return;
        }
        queueIndex -= priorityQueue.length;
        povertyQueue.splice(queueIndex, 1);

    }
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

// OnLoad initialization

window.onload = function () {
    initCanvases();
    window.addEventListener('resize', resize);
    listen('cbtn', 'click', showHideControls);
    window.addEventListener('click', canvasClicked);
    initWheelCanvas();
    resize();
    Update();
};

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

//#endregion Utils and Helpers