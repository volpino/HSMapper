$.editable.addInputType('manytomany', {
    element : function(settings, original) {
        var input = $('<input />').autocomplete(settings.autocomplete);
        $(this).append(input);
        return(input);
    }
});
