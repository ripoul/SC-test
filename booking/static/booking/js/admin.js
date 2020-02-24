$(document).ready(function () {
    $('#form_add_rt').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: e.target.action,
            data: $(this).serialize(),
            type: e.target.method,
            success: function (data) {
                $('#modal_add_rt').modal('hide');
                data = JSON.parse(data)
                id = data[0].pk
                name = data[0].fields.name
                newLigne = `<tr><th scope=\"row\">${id}</th><td>${name}</td><td><a href=\"/booking/rt/view/${id}\">Modifie</a></td></tr>`
                $('#table_rt > tbody:last-child').append(newLigne);
            }
        });
    });
});
