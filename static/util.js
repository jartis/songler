function makeToast(cat, msg) {
    let toastid = 'toast' + Math.floor(Math.random() * 256).toString(16);
    let toast = '<div class="toast" id="' + toastid + '" role="alert" aria-live="assertive" aria-atomic="true">';
    toast += '<div class="toast-header">';
    //toast += '<img src="';
    // Add a toast icon here!
    //toast += '" class="rounded me-2">';
    toast += '<strong class="me-auto">' + cat + '</strong>';
    toast += '<button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>';
    toast += '</div>';
    toast += '<div class="toast-body">';
    toast += msg;
    toast += '</div></div>';
    document.getElementById('toaster').innerHTML += toast;
    let toastEl = bootstrap.Toast.getOrCreateInstance(document.getElementById(toastid));
    toastEl.show();
}