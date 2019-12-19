$(".custom-file-input").on("change", function () {
    $(this).next(".custom-file-label").html($(this)[0].files[0].name);
});

$('.file-upload').on('click', function () {
    var files = document.getElementById("customFile").files;
    if (files.length == 1) {
        var file_size = document.getElementById("customFile").files[0].size;
        if (0 < file_size && file_size < 1024 * 1024) {
            var form = document.getElementById("upload-file-form");
            form.submit();
        }
        else {
            $(".error-message").addClass("alert-danger");
            $(".error-message").html("<strong>Alert!</strong> - This function can upload under 1 MB file.");

        }
    }
    else {
        $(".error-message").addClass("alert-danger");
        $(".error-message").html("<strong>Alert!</strong> - Please upload only one file.");

    }
});

$('.share-upload').on('click', function () {
    var form = document.getElementById("upload-share-form");
    form.submit();
});