//using jQuery
$('.js-vote').click(function(ev) {
    let $this = $(this),
        type = $this.data('type'),
        id = $this.data('id'),
        action = $this.data('action');
        $.ajax('/vote/', {
        method: 'POST',
        data: {
            type: type,
            id: id,
            action: action,
        },
    }).done(function(data) {
        $('#rating-' + id).text("r:" + data.rating);
    });
    console.log(type + " " + id + ": " + action);
})

$('.js-not-authorized').click(function(ev) {
    alert("Please log in");
})


$('.js-correct').click(function(ev) {
    let $this = $(this),
        id = $this.data('id');
    $.ajax('/correct/', {
        method: 'POST',
        data: {
            id: id,
        },
    }).done(function(data) {
        $('#correct-' + id).prop('checked', data.action);
    });
    console.log("Correct is " + id);
})