$(document).ready(function () {
    $('.form_delete_reservation').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: e.target.action,
            data: $(this).serialize(),
            type: "POST",
            success: function (data) {
                e.target.closest("tr").remove();
            }
        });
    });
});