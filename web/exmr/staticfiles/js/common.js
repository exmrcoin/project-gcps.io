
function getCurrentLanguage() {
    var lang = window.location.pathname.split("/")[1]
    return "/"+lang
}

function formSubmit(formId, url) {
    var result = false;
    lang = getCurrentLanguage()
    url = lang + url
    var data = $(formId + " :input").serializeArray();
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        async: false,
        dataType: 'json',
        success: function (data) {
            if (data.msg) {
                $.toaster(data.msg, 'Success', 'success');
                result = true;
            }
            else {
                $.each(data, function (key, value) {
                    var $input = $(formId).find(":input[name='" + key + "']");
                    $input.siblings(".error").html(value[0]).show();
                });
                result = false;
            }
        }
    });
    return result;
}
