$(document).ready(() => {

    $("#username").on('input', () => {
        let username = $("#username").val();
        
        let xhr = new XMLHttpRequest();

        // xhr.open('GET', `${document.location.host}/api/username-availability?username=${username}`, true)
        xhr.open('GET', `http://127.0.0.1:5000/api/username-availability?username=${username}`, true)

        xhr.onload = function() {
            if (this.status == 200) {
                isTaken = this.responseText;

                if (username.length > 2 && username.length < 21) {
                    if (isTaken == 'true') {
                        $("#username-avail").text('Username is taken');
                    } else {
                        $("#username-avail").text('Username available');
                    }
                } else {
                    $("#username-avail").text('');
                }
            }
        };

        xhr.send();
    });
});