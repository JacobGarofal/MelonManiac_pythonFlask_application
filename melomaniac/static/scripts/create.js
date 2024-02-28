$(document).ready(function() {
    const $freeEventCheck = $('#freeEventCheck');
    const $ticketPriceCollapsible = $('#ticketPriceCollapsible');

    $freeEventCheck.on('change', function() {
        if ($freeEventCheck.prop('checked')) {
            $ticketPriceCollapsible.removeClass('show');
        } else {
            $ticketPriceCollapsible.addClass('show');
        }
    });
});

