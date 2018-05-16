
function getCurrentLanguage() {
    var lang = window.location.pathname.split("/")[1];
    return "/" + lang
}

function formSubmit(formId, url) {
    var result = false;
    var lang = getCurrentLanguage();
    var data = $(formId + " :input").serializeArray();
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        async: false,
        dataType: 'json',
        success: function (data) {
            if (data.msg) {
                // $.toaster(data.msg, 'Success', 'success');

                $.notify({
                    icon: 'fa fa-warning-sign',
                    title: 'Success',
                    message: "Form Submitted Successfully"
                }, {
                        animate: {
                            enter: 'animated fadeInRight',
                            exit: 'animated fadeOutRight'
                        },

                        type: 'success'

                    });
                result = true;
            }
            else {
                var count = 500;
                $.each(data, function (key, value) {
                    var $input = $(formId).find(":input[name='" + key + "']");
                    $input.addClass('error-focus');
                    $input.siblings(".error").html(value[0]).show();
                    window.setTimeout(function () {
                    $.notify({
                        icon: 'fa fa-warning-sign',
                        title: 'warning',
                        message: value[0]
                    }, {
                            animate: {
                                enter: 'animated fadeInDown',
                                exit: 'animated fadeOutDown'
                            },
    
                            type: 'danger'
    
                        });
                    }, count);
                    count += 500;
                });
                result = false;
            }
        }
    });
    return result;
}
