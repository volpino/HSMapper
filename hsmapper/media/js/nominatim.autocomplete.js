$(function() {
  $.nominatim = function(expr, options) {
    $(expr).autocomplete({
      source: function( request, response ) {
        $.ajax({
          url: "http://open.mapquestapi.com/nominatim/v1/search",
          dataType: "jsonp",
          jsonp: "json_callback",
          data: {
            format: "json",
            q: request.term
          },
          success: function( data ) {
            response( $.map( data, function( item ) {
              item.label = item.display_name;
              item.value = item.display_name;
              return item;
            }));
          }
        });
      },
      minLength: options.minLength || 2,
      delay: options.delay || 200,
      select: function( event, ui ) {
        console.log(ui.item);
        if (options.select && ui.item) {
          options.select(ui.item);
        }
      },
      open: function() {
        $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
      },
      close: function() {
        $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
      }
    });
  }
});
