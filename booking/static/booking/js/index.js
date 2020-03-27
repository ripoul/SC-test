$(document).ready(function () {
    $("#table_reservation").on("submit", '.form_delete_reservation', function (e) {
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
    $('.form_add_reservation').on("submit", function (e) {
        e.preventDefault();
        $.ajax({
            url: e.target.action,
            data: $(this).serialize(),
            type: "POST",
            success: function (data) {
                $('.modal').modal('hide');
            },
            error: function (data) {
                alert(data.responseText)
            }
        });
    });

    let socketURL = (window.location.protocol).includes('https') ? "wss://" : "ws://";
    socketURL = socketURL.concat(window.location.host + "/ws");
    let socket = new WebSocket(socketURL);

    socket.onopen = function (e) {
    };

    socket.onmessage = function (event) {
        data = JSON.parse(event.data)
        id_reservation = data[0].pk
        title = data[0].fields.title
        start_date = data[0].fields.start_date
        end_date = data[0].fields.end_date
        resource = data[0].fields.resource[0]
        resource_location = data[0].fields.resource[1]
        owner = data[0].fields.owner[0]
        if (owner == currentUser || isSuperuser) {
            form = `
                <form class="form_delete_reservation" action="${reservationDeleteURL}">
                <input id="id" name="id" class="form-control" type="text" value="${id_reservation}" required
                    hidden readonly>
                ${csrf}
                <div class="form-group">
                    <button type="submit" class="btn btn-primary btn-block"> ${deleteValue} </button>
                </div> <!-- form-group// -->
            </form>
                `
            newLigne = `<tr><th scope=\"row\">${id_reservation}</th><td>${title}</td><td>${start_date}</td><td>${end_date}</td><td>${resource}</td><td>${resource_location}</td><td>${form}</td></tr>`
            $('#table_reservation > tbody:last-child').append(newLigne);
        } else {
            newLigne = `<tr><th scope=\"row\">${id_reservation}</th><td>${title}</td><td>${start_date}</td><td>${end_date}</td><td>${resource}</td><td>${resource_location}</td><td>Not Yours</td></tr>`
            $('#table_reservation > tbody:last-child').append(newLigne);
        }

    };
});
