var artistInfo = {};

window.onload = function () {
    const req = new XMLHttpRequest();
    req.onload = function () {
        artistInfo = JSON.parse(this.responseText);
        writeArtistInfo();
    };
    req.open('GET', APIURL + '/artistinfo/' + aid);
    // }
    req.send();
};

function writeArtistInfo() {
    document.getElementById('headline').innerText = artistInfo.artist;
    let si = '';
    // What songs does this artist have?
    if (artistInfo.songs.length > 0) {
        si += '<hr>';
        si += `<h3>Songs by ${artistInfo.artist}:</h3>`;
        for (let i = 0; i < artistInfo.songs.length; i++) {
            si += `<p><a href="/songs/${artistInfo.songs[i].sid}">${artistInfo.songs[i].title}</a></p>`;
        }
        si += '<hr>';
        if (artistInfo.users.length > 0) {
            si += `<h3>Users who play songs by ${artistInfo.artist}:</h3>`;
            for (let i = 0; i < artistInfo.users.length; i++) {
                si += '<p><a href="/profile/' + artistInfo.users[i].username + '">' + artistInfo.users[i].username + '</a></p>';
                // TODO: Add link to songlist?
            }
        } else {
            si += `<p>No users with ${artistInfo.artist} on their public song list.</p>`;
        }
    } else {
        si += `<p>No songs by ${artistInfo.artist}.</p>`;
    }
    document.getElementById('artistinfo').innerHTML = si;
}