$(document).ready(function() {
    var $collapseElement = $('#advancedFilters');
    var $toggleButton = $('#toggleButton');
    var $toggleIcon = $('#toggleIcon');

    var bsCollapse = new bootstrap.Collapse($collapseElement[0], { toggle: true });

    $collapseElement.on('show.bs.collapse', function() {
        $toggleButton.text("Fewer search options ").append($toggleIcon);
        $toggleIcon.removeClass().addClass("fas fa-chevron-up");
    });

    $collapseElement.on('hide.bs.collapse', function() {
        $toggleButton.text("More search options ").append($toggleIcon);
        $toggleIcon.removeClass().addClass("fas fa-chevron-down");
    });
})