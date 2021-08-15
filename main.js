// Here's a crappy sample songlist while I test things out

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
        wheelCtx.arc(400, 400, 350, -(slice/2), slice/2, false);
        wheelCtx.lineTo(400, 400);
        wheelCtx.fill();
        // Draw song label
        let displayName = songlist[i][0] + ' - ' + songlist[i][1];
        fitTextToWidth(wheelCtx, displayName, 250);
    }

    srcctx.drawImage(wheelCanvas, 560, 140);
}

function boundedRandomColor() {
    let r = Math.floor(Math.random() * 150) + 50;
    let g = Math.floor(Math.random() * 150) + 50;
    let b = Math.floor(Math.random() * 150) + 50;
    return '#' + r.toString(16) + g.toString(16) + b.toString(16);
}

function fitTextToWidth(context, textToFit, maxWidth) {
    txtSizeTop = 100;
    context.font = txtSizeTop + 'px Arial'; // TODO: Font selection?
    while (context.measureText(textToFit).width > maxWidth) {
        txtSizeTop--;
        if (txtSizeTop < 8) break;
        context.font = txtSizeTop + 'px Arial'; // TODO: Font selection?
    }
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillStyle = '#000000';
    context.fillText(textToFit, 601, 401);
    context.fillStyle = '#FFFFFF';
    context.fillText(textToFit, 600, 400);
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
    dstctx.fillStyle = '#00FF00';
    dstctx.fillRect(0, 0, dstCanvas.width, dstCanvas.height);
    dstctx.drawImage(srcctx.canvas, 0, 0, 1920, 1080, screenOffsetX, screenOffsetY, newWidth, newHeight);
}

// OnLoad initialization

window.onload = function () {
    initCanvases();
    window.addEventListener('resize', resize);
    listen('cbtn', 'click', showHideControls);
    initWheelCanvas();
    resize();
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
    srcctx.fillStyle = '#00FF00';
    srcctx.fillRect(0, 0, 1920, 1080);

    dstCanvas = document.getElementById('canvas');
    dstCanvas.width = window.innerWidth;
    dstCanvas.height = window.innerHeight;
    dstctx = dstCanvas.getContext('2d');
    dstctx.fillStyle = '#00FF00';
    dstctx.fillRect(0, 0, dstCanvas.width, dstCanvas.height);
}

//#endregion Utils and Helpers