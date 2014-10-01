var header = '';
var $qrcode = $('#qrcode');
var $filepicker = $('#filepicker');
var loggedin = false;
var token = '';

$(function() {
    $('input').click(function() { this.select(); });

    poll = setInterval(checkAuth, 5000);

    $(':file').change(function() {
        putFile(this.files[0]);
    });

    var filepicker = $('#dropzone');

    filepicker.on('dragover', function() {
        $(this).css('background', 'blue');
    });

    filepicker.on('dragleave', function() {
        $(this).css('background', 'red');
    })

    $('#logout').click(disableToken);
});

var checkAuth = function() {
    $.getJSON('/get', function(r) {
        if (r.authorized == 'true') {
            if (!loggedin) {
                $qrcode.toggle();
                $filepicker.toggle();
                loggedin = true;
                console.log('gonna get token asap');
                getToken();
                // flash logged in
            }
        }
        else {
            if (loggedin) {
                $qrcode.toggle();
                $filepicker.toggle();
                loggedin = false;
                // flash logged out, clear token
            }
            console.log('still waiting')
        }
    });
}

var getToken = function() {
    $.getJSON('/get/token', function(r) {
        token = r.token;
        header = {Authorization: 'Bearer ' + token};
        console.log('got token');
    });
}

var getAccName = function() {
    $.ajax({
        url: 'https://api.dropbox.com/1/account/info',
        type: 'GET',
        headers: header,
        dataType: 'json',
        success: function(r) {
            console.log(r.display_name);
        }
    });
}

var disableToken = function() {
    $.ajax({
        url: 'https://api.dropbox.com/1/disable_access_token',
    type: 'POST',
    headers: header,
    dataType: 'json',
    success: function(r) {
        console.log('logged out');
        logeedin = false;
    }
    });
}

var putFile = function(file) {
    $.ajax({
        url: 'https://api-content.dropbox.com/1/files_put/auto/' + file.name,
    type: 'PUT',
    headers: $.extend({}, header),
    dataType: 'json',
    data: file,
    processData: false,
    contentType: file.type,
    success: function(r) {
        console.log(r.path.split('/').slice(-1) + ' ' + r.size);
    }
    });
}
