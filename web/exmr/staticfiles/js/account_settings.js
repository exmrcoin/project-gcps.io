$(function() {
    var clipboard = new ClipboardJS('.share');

    clipboard.on('success', function(e) {

        $('.share').text(' Copied!!');

        e.clearSelection();
    });

    function formSubmit(formId, url) {

        var data = $(formId + " :input").serializeArray();
        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            dataType: 'json',
            success: function (data) {
                if (data.msg) {
                    $(formId).siblings('.alert').text(data.msg)
                    $(formId).siblings('.alert').addClass('alert-success')
                }
                else {
                    $.each(data, function (key, value) {
                        var $input = $(formId).find("input[name='" + key + "']");
                        $input.siblings(".error").html(value[0]).show();
                    });
                }
            }
        });

    }
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

    });