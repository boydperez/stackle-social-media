$(document).ready(() => {

    // Print-debug
    console.log('test follow.js');

    $(".follow-btn").on('click', (event) => {
        $.ajax({
            url: `/api/follow/${userId}`,
            method: 'GET',
            async: true,
            crossDomain: true,
            dataType: 'json',
        }).done((responseData, responseText) => {
            console.log(responseData);
            let followBtn = event.target;

            if (responseData.message == 'followed') {
                followBtn.classList.add('following');
                followBtn.classList.remove('follow');
                console.log('followed!');
            } else {
                followBtn.classList.remove('following');
                followBtn.classList.add('follow');
                console.log('unfollowed!');
            }
        });
    });
});
