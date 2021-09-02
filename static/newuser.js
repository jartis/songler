function validateForm() {
    let newusername = document.forms.newuser.username.value;
    let email = document.forms.newuser.email.value;
    let pass = document.forms.newuser.password.value;
    let passconf = document.forms.newuser.passwordconf.value;

    if (pass != passconf) {
        makeToast(ERROR, '⚠️ Error', 'Passwords do not match.');
        return false;
    }

    const ureq = new XMLHttpRequest();
    ureq.open('GET', APIURL + '/checkuser/' + newusername, false);
    ureq.send();
    if (ureq.responseText == '1') {
        makeToast(ERROR, '⚠️ Error', 'Username is already in use.');
        return false;
    }

    const ereq = new XMLHttpRequest();
    ereq.open('GET', APIURL + '/checkemail/' + email, false);
    ereq.send();
    if (ereq.responseText == '1') {
        makeToast(ERROR, '⚠️ Error', 'Email is already in use.');
        return false;
    }
}