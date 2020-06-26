$(function() {
    var clipboard = new ClipboardJS('.share');

    clipboard.on('success', function(e) {

        $('.share').text(' Copied!!');

        e.clearSelection();
    });

    $('#publicInfo').on('input',function(e){
        $(this).find('.error').text('')
    });

    $('#publicInfo').on('submit', function(e) {
        e.preventDefault();
        formSubmit('#publicInfo', '/save-public-info/');
    });

    $('#accountForm').on('submit', function(e) {
        e.preventDefault();
        formSubmit('#accountForm', '/settings/');
    });

    $('#accountForm').on('input',function(e){
        $(this).find('.error').text('')
    });

    $('#securityForm').on('submit', function(e) {
        e.preventDefault();
        formSubmit('#securityForm', '/save-security-info/');
    });

    $('#securityForm').on('input',function(e){
        $(this).find('.error').text('')
    });

    $('#merchantSettingsForm').on('submit', function(e) {
        e.preventDefault();
        formSubmit('#merchantSettingsForm', '/save-ipn-settings/');
    });

    $('#merchantSettingsForm').on('input',function(e){
        $(this).find('.error').text('')
    });

    });

