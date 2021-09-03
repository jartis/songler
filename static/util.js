const APIURL = '/api/v1';
const ERROR = 0;
const SUCCESS = 1;
const INFO = 2;

function makeToast(cat, hed, msg) {
    let toastid = 'toast' + Math.floor(Math.random() * 256 * 256).toString(16);
    let toast = '<div class="toast" id="' + toastid + '" role="alert" aria-live="assertive" aria-atomic="true">';
    toast += '<div id="toasthead' + toastid + '" class="toast-header">';
    //toast += '<img src="';
    // Add a toast icon here!
    //toast += '" class="rounded me-2">';
    toast += '<strong class="me-auto">' + hed + '</strong>';
    toast += '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>';
    toast += '</div>';
    toast += '<div class="toast-body">';
    toast += msg;
    toast += '</div></div>';
    document.getElementById('toaster').innerHTML += toast;
    switch (cat) {
        case ERROR:
            document.getElementById('toasthead' + toastid).classList.add("bg-danger");
            document.getElementById('toasthead' + toastid).classList.add("text-light");
            break;
        case SUCCESS:
            document.getElementById('toasthead' + toastid).classList.add("bg-success");
            document.getElementById('toasthead' + toastid).classList.add("text-light");
            break;
    }
    let toastEl = bootstrap.Toast.getOrCreateInstance(document.getElementById(toastid));
    toastEl.show();
}

function titleCase(str) {
    return str.toLowerCase().split(' ').map(function (word) {
        return (word.charAt(0).toUpperCase() + word.slice(1));
    }).join(' ');
}

function removeArticles(str) {
    words = str.split(" ");
    if (words.length <= 1) return str;
    if (words[0] == 'A' || words[0] == 'The' || words[0] == 'An')
        return words.splice(1).join(" ");
    return str;
}

function TitleCompare(a, b) {
    return removeArticles(titleCase(a)).localeCompare(removeArticles(titleCase(b)));
}