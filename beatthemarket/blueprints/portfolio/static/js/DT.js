$(document).ready(function () {

    $('#date').keyup(function () {
        $(this).val($(this).val().replace(/(\d{4})\-?(\d{2})\-?(\d{2})/, '$1-$2-$3'))
    });

    $('#ticker').keyup(function () {
        $(this).val($(this).val().toUpperCase())
    });

    $('#my-holdings').dataTable({

        columnDefs: [{
            orderable: false,
            className: 'select-checkbox',
            targets: 0
        }],
        select: {
            style: 'os',
            selector: 'td:first-child'
        }
    })

    $('tbody.tbody').on('click', 'span.remove', function (e) {
        $(this).parent().parent().remove()
    })

});
