$(function() {
$.ajax({
    type: "GET",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    async: true,
    url: '/autocomplete'
    }).done(function (data) {
        $('#autocomplete').autocomplete({
            source: data.json_list,
            minLength: 3,
        });
    });
});

function postPlaylist() {
    var track_and_artist = document.getElementById("autocomplete").value;
    console.log(track_and_artist);
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: "/playlist",
        dataType: "json",
        async: true,
        data: JSON.stringify({'track_and_artist': track_and_artist}),
        success: function (results) {
            console.log("Success")
            $('html, body').animate({ scrollTop: 0 }, 'fast');
            $(tracks).empty();
            $(track_container).empty();
            $('#export_container').empty();
            for (i = 0; i < 10; i++){
                var track_name = results['playlist'][i][0];
                var artist_name = results['playlist'][i][1];
                var li = document.createElement('li');

                li.setAttribute('id', 'track');
                li.setAttribute('type', 'submit');
                li.setAttribute('onclick', 'postTrackInfo(this.innerText)');
                li.value = i;
                li.innerText = track_name + ' by ' + artist_name;

                var container = document.getElementById('tracks');
                container.append(li);

                $('li').click(function(){
                    $('.highlight').removeClass('highlight');
                    $(this).addClass('highlight');
                    $('li').addClass('hover');
                    $('li').removeClass('playing');
                    $(this).removeClass('hover');
                    clearTimeout(t);
                    clearInterval(id);
                });
            }
        },
        error: function(error) {
            console.log("failure")
        }
    })
}

function postTrackInfo(clicked_text) {
    console.log(clicked_text);
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: "/track_info",
        dataType: "json",
        async: true,
        data: JSON.stringify({'track_and_artist': clicked_text}),
        success: function (results) {
            console.log("Success")
            $('html, body').animate({ scrollTop: 0 }, 'fast');
            $(track_container).empty();
            var album_art = results['track_info'][0];
            var track_name = results['track_info'][1];
            var artist_name = results['track_info'][2];
            var lyrics = results['track_info'][3];

            var img = document.createElement('img');
            img.setAttribute('src', album_art);
            img.setAttribute('id', 'album_art');
            img.setAttribute('onclick', 'play_preview()');
            img.setAttribute('value', track_name + ' by ' + artist_name);

            var bar = document.createElement('div');
            bar.setAttribute('id', 'progress_bar');

            var bar_container = document.createElement('div');
            bar_container.setAttribute('id', 'progress_bar_container');

            bar_container.appendChild(bar)

            var container = document.getElementById('track_container');
            container.prepend(img);
            container.appendChild(bar_container);

            var track_info = document.createElement('div');

            var track = document.createElement('p');
            var artist = document.createElement('p');

            track_info.setAttribute('id', 'track_info');
            track.setAttribute('style', 'line-height: 30px;');
            track.innerText = track_name;
            artist.innerText = artist_name;

            track.setAttribute('style', 'font-size: 34px;line-height:32px;margin-top:15px;margin-bottom:0px');
            artist.setAttribute('style', 'font-size: 20px;line-height:0;');

            track_info.appendChild(track);
            track_info.appendChild(artist);

            container.append(track_info);

            var lyrics_div = document.createElement('div');
            var lyrics_p = document.createElement('p');
            lyrics_div.setAttribute('id', 'lyrics');

            lyrics_p.innerText = lyrics;
            lyrics_div.appendChild(lyrics_p);
            container.append(lyrics_div);

        },
        error: function(error) {
            console.log("failure")
        }
    })
}

var t;
var count;

function countdown() {
    if (count === -1) {
        $('.highlight').removeClass('playing');
        $('#album_art').css('border', '3px solid black');
    } else {
        count--;
        t = setTimeout(countdown, 1000);
    }
}

var id;

function move() {
    var elem = document.getElementById('progress_bar');
    console.log('moving');
    var width = 0;
    id = setInterval(frame, 100);
    function frame() {
        if (width >= 290) {
            clearInterval(id);
        } else {
            width++;
            elem.style.width = width/2.9 + '%';
        }
    }
}

function play_preview() {
    var track_and_artist = document.getElementById("album_art").getAttribute('value');
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: "/track_preview",
        dataType: "json",
        async: true,
        data: JSON.stringify({'track_and_artist': track_and_artist}),
        success: function (results) {
            console.log("Album Clicked");
            var preview_url = results['preview_url'];
            if (preview_url == null) {
                console.log('NO PREVIEW URL');
                $('#progress_bar_container').css('background-color', 'grey');
            }
            else {
                $('#track_container').append('<audio id="embed_player" src=" '+ results['preview_url'] +' " hidden="true"></audio>');
                var audio = document.getElementById('embed_player');
                audio.volume = 0.15;

                if (audio.paused) {
                    console.log('Audio Played');
                    audio.play();
                    $('.highlight').addClass('playing');
                    $('#album_art').css('border', '3px solid #ec0356');
                    count = 29;
                    countdown();
                    move();
                }

                else{
                    clearTimeout(t);
                    clearInterval(id);
                    console.log('Audio Paused');
                    audio.pause();
                    audio.currentTime = 0;
                    $('.highlight').removeClass('playing');
                    $('#album_art').css('border', '3px solid black');
                    $('#progress_bar').css('width', '0%');
                }
            }
        },
        error: function(error) {
            console.log("failure");
        }
    })

}