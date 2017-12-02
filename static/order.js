$("#myselect").on("change", function() {
    $("#" + $(this).val()).show().siblings();
});

$("#departurebutton").on("click", function (e) {
    e.stopPropagation();
    let airport = document.getElementById("airport").value;
    let date = document.getElementById("date").value;
    let otime = document.getElementById("otime").value;
    let number = document.getElementById("number").value;
    let departureetime = document.getElementById("departureetime").value;
    let location = document.getElementById("location").value;
    alert("Submitted");
    return($.post("/", {'airport': airport, 'date': date, 'otime': otime, 'number': number, 'departureetime': departureetime, 'location': location, 'type': 0}));
});

$("#arrivalbutton").on("click", function (e) {
    e.stopPropagation();
    let airport = document.getElementById("airport").value;
    let date = document.getElementById("date").value;
    let otime = document.getElementById("otime").value;
    let number = document.getElementById("number").value;
    let arrivaletime = document.getElementById("arrivaletime").value;
    alert("Submitted");
    const data = {'airport': airport, 'date': date, 'otime': otime, 'number': number, 'arrivaletime': arrivaletime, 'type': 1}
    $.post("/order", data, function (data) {
        // if ()
        if (data.error) {
            alert("fuck that didnt work")
        } else {
            location.href = "/"
        }
    })

    return false
});