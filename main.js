// Here's a crappy sample songlist while I test things out

const BLACK = '#000000';
const WHITE = '#FFFFFF';
const GREEN = '#00FF00';

var songlist = [
    ["The Beatles", "Blackbird"],
    ["Green Day", "Basket Case"],
    ["Dr. Hook", "The Wonderful Soup Stone"],
    ["Stan Rogers", "The Mary Ellen Carter"],
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

// Set up a drawing target for the wheel
var wheelCanvas;
var wheelCtx;
var wheelRotation = 0;
var wheelVelocity = 0;
var songIndex = 0;
var REMOVE = 0; // Pull an option after it is selected, on a new spin

function initWheelCanvas() {
    wheelCanvas = document.createElement('canvas');
    wheelCanvas.width = 800;
    wheelCanvas.height = 800;
    wheelCtx = wheelCanvas.getContext('2d');
    wheelCtx.fillStyle = '#00000000';
    wheelCtx.fillRect(0, 0, 800, 800);

    let count = songlist.length;
    for (let i = 0; i < count; i++) {
        wheelCtx.fillStyle = boundedRandomColor();
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
    context.fillStyle = BLACK;
    context.fillText(textToFit, 601, 401);
    context.fillStyle = WHITE;
    context.fillText(textToFit, 599, 399);
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
    if (wheelVelocity == 0 && songlist.length > 1) {
        srcctx.font = '16px Arial';
        srcctx.textAlign = 'center';
        srcctx.textBaseline = 'middle';
        srcctx.fillStyle = WHITE;
        srcctx.fillText('CLICK', 960, 520);
        srcctx.fillText('TO', 960, 540);
        srcctx.fillText('SPIN', 960, 560);
        srcctx.fillText('CLICK', 961, 520);
        srcctx.fillText('TO', 961, 540);
        srcctx.fillText('SPIN', 961, 560);
    }

    DrawScreen();
}

function spinWheel() {
    if (REMOVE == 1 && songlist.length > 1) {
        songlist.splice(songIndex, 1);
    }
    initWheelCanvas();
    wheelVelocity = 20 + (10 * Math.random());
    if (REMOVE == 0) {
        REMOVE = 1;
    }
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
            songIndex = Math.floor((360 - wheelRotation + (sliceSize/2)) / sliceSize);
        }
    }
    window.requestAnimationFrame(Update);
}

function canvasClicked(e) {
    let mx = ((e.clientX - screenOffsetX) / (newWidth)) * 1920;
    let my = ((e.clientY - screenOffsetY) / (newHeight)) * 1080;
    if (wheelVelocity == 0 && songlist.length > 1) {
        if (mx > (960 - 45) && mx < (960 + 45) && my > (540 - 45) && my < (540 + 45)) {
            spinWheel();
        }
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

//#endregion Utils and Helpers