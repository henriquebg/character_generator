$(document).ready(function() 
{
	$('[data-toggle="tooltip"]').tooltip(); 
	
    $("#slider-sec-minima").slider({
        animate: true,
        value:0,
        min: 0.01,
        max: 0.25,
        step: 0.01,
        slide: function(event, ui) {
            $('#slider-sec-minima a').html('<label><span class="glyphicon glyphicon-chevron-left"></span> ' + ui.value + ' <span class="glyphicon glyphicon-chevron-right"></span></label>');
            $('#sec-minima').val(ui.value);
        }
    });

    $("#slider-sec-maxima").slider({
        animate: true,
        value:0,
        min: 0.25,
        max: 0.50,
        step: 0.01,
        slide: function(event, ui) {
            $('#slider-sec-maxima a').html('<label><span class="glyphicon glyphicon-chevron-left"></span> ' + ui.value + ' <span class="glyphicon glyphicon-chevron-right"></span></label>');
            $('#sec-maxima').val(ui.value);
        }
    });
    
    $('#slider-sec-minima a').html('<label><span class="glyphicon glyphicon-chevron-left"></span> ' + 0.01 + ' <span class="glyphicon glyphicon-chevron-right"></span></label>');
    $('#slider-sec-maxima a').html('<label><span class="glyphicon glyphicon-chevron-left"></span> ' + 0.25 + ' <span class="glyphicon glyphicon-chevron-right"></span></label>');
});