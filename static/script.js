$(function() {
  box = {}; // global for debugging
  var $card = $('.card');

  var checkAuth = function() {
    console.log('polling');
    $.getJSON('/get', function(r) {
      if (r.authorized == 'true') {
        if (!box.loggedin) {
          box.loggedin = true;
          console.log('gonna get token asap');
          getToken();
          getName();
          $card.addClass('flipped');
        }
      }
      else if (box.loggedin) {
        box.loggedin = false;
        $card.removeClass('flipped');
      }
    });
  };

  var getToken = function() {
    $.getJSON('/get/token', function(r) {
      box.header = {Authorization: 'Bearer ' + r.token};
      console.log('got token');
    });
  };

  var logout = function() {
    $.getJSON('/logout', function(r) {
      $card.removeClass('flipped');
      box = {};
      console.log('logged out');
    });
  };

  var getName = function() {
    $.getJSON('https://api.dropbox.com/1/account/info', function(r) {
      box.name = r.display_name;
      console.log('welcome ' + box.name);
    });
  };

  var putFile = function(file) {
    $.ajax({
      url: 'https://api-content.dropbox.com/1/files_put/auto/' + file.name,
      type: 'PUT',
      headers: box.header,
      dataType: 'json',
      data: file,
      processData: false,
      contentType: file.type,
      success: function(r) {
        console.log(r.path.split('/').slice(-1) + ' ' + r.size);
      },
      failure: function() { console.log('upload failed'); }
    });
  };

  var makeDropzone = function(element, input) {
    element.addEventListener('dragover', function(e) {
      console.log('dragover');
      e.stopPropagation();
      e.preventDefault();
    });

    element.addEventListener('dragenter', function(e) {
      console.log('dragenter');
      e.stopPropagation();
      e.preventDefault();
    });

    element.addEventListener('drop', function(e) {
      console.log('dropped');
      e.preventDefault();
      handleFiles(e.dataTransfer.files);
      return false;
    });

    element.addEventListener('click', function(e) {
      console.log('clicked');
      input.click();
    });

    input.addEventListener('change', function() {
      handleFiles(input.files);
      $('form').trigger('reset');
    });
  };

  handleFiles = function(files) {
    for (var i=0; i<files.length; i++) {
      var file = files[i];
      console.log('it\'s a file: ' + file.name);
      putFile(file);
      // show a progress bar or something?
    }
  };

  $('.link input').click(function() { this.select(); }); // select auth link

  $('.logout').click(logout);

  makeDropzone(document.getElementsByClassName('dropzone')[0],
      document.getElementsByTagName('input')[1]);

  var poll = setInterval(checkAuth, 5000); // default to 5000
});

