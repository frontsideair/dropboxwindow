var client = new Dropbox.Client({ key: "" });

// authenticate user by polling access token

var showError = function(error) {
    switch (error.status) {
        case Dropbox.ApiError.INVALID_TOKEN:
            // access token problem
            break;

        case Dropbox.ApiError.NOT_FOUND:
            // folder not there
            break;

        case Dropbox.ApiError.OVER_QUOTA:
            // over quota
            break;

        case Dropbox.ApiError.RATE_LIMITED:
            // try later
            break;

        case Dropbox.ApiError.NETWORK_ERROR:
            // network problem
            break;

        default:
            // INVALID_PARAM, OAUTH_ERROR, INVALID_METHOD, etc.
            // do something appropriate
    }
};

client.onError.addListener(function(error) {
    showError(error);
});

client.getAccountInfo(function(error, accountInfo) {
    // handle error
    // print accountInfo.name
});

var pickedFile = {"name": "", "data": ""}; // use filepicker

client.writeFile(pickedFile.name, pickedFile.data, function(error, stat) {
    // handle error
    // alert file written
});
