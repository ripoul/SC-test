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
    $('.form_add_reservation').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: e.target.action,
            data: $(this).serialize(),
            type: "POST",
            success: function (data) {
                data = JSON.parse(data)
                id_reservation = data[0].pk
                title = data[0].fields.title
                start_date = data[0].fields.start_date
                end_date = data[0].fields.end_date
                resource = data[0].fields.resource[0]
                resource_location = data[0].fields.resource[1]
                newLigne = `<tr><th scope=\"row\">${id_reservation}</th><td>${title}</td><td>${start_date}</td><td>${end_date}</td><td>${resource}</td><td>${resource_location}</td><td></td></tr>`
                $('#table_reservation > tbody:last-child').append(newLigne);
                $('.modal').modal('hide');
            },
            error: function (data) {
                alert(data.responseText)
            }
        });
    });
});
