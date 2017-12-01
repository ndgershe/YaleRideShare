$("#myselect").on("change", function() {
    $("#" + $(this).val()).show().siblings();
});

let airport = document.getElementById("airport").value;
let date = document.getElementById("date").value;
let otime = document.getElementById("otime").value;
let number = document.getElementById("number").value;

function departure()
{
    let etime = document.getElementById("departureetime").value;
    $.post("/order", {airport: airport, date: date, otime: otime, number: number, etime: etime});
}

function arrival()
{
    let etime = document.getElementById("arrivaletime").value;
    $.post("/order", {airport: airport, date: date, otime: otime, number: number, etime: etime});
}