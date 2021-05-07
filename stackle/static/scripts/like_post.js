$(document).ready(() => {

    // Print-debug
    console.log('test like_post');

    $(".heart").on('click', (event) => {
        
        /* let xhr = new XMLHttpRequest();

        // Get the value of the .like-btn id
        let postId = event.target.id;
        // xhr.open('GET', `http://127.0.0.1:5000/api/like-post/${postId}`, true)
        xhr.open('GET', `/api/like-post/${postId}`, true)

        // xhr.setRequestHeader('XSRF-TOKEN', csrf)

        xhr.onload = function() {
            if (this.status == 200) {
                console.log(this.responseText);
            }
        };

        xhr.send();
    }); */

        const likeBtn = $(this);

        let postId = event.target.id;

        $.ajax({
            url: `/api/like-post/${postId}`,
            method: 'POST',
            async: true,
            crossDomain: true,
            dataType: 'json',
        }).done((responseData, responseText) => {
            console.log(responseData);

            if (responseData.message == 'post liked') {
                console.log('liked!')
                let likeBtn = event.target;
                likeBtn.classList.add('fa-heart')
                likeBtn.classList.remove('fa-heart-o')
                $(likeBtn).siblings('.like-counter').text((i, origText) => {
                    return parseInt(origText) + 1;
                })
            } else {
                console.log('unliked!')
                let likeBtn = event.target;
                likeBtn.classList.add('fa-heart-o')
                likeBtn.classList.remove('fa-heart')
                $(likeBtn).siblings('.like-counter').text((i, origText) => {
                    return parseInt(origText) - 1;
                })
            }
        });


        // TODO: Handle real time post modifiers
    });
});