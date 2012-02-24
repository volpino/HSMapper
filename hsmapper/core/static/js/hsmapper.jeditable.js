function save_feature_edit(value, settings) {
  var display_msg = $(this).find("option[value='"+value+"']").text() || value;
  if (settings.checkbox && settings.checkbox.trueValue) {
    value = (value === settings.checkbox.trueValue) ? 1 : 0;
  }
  var type = $(this).parent().attr("type");
  var d = {}
  d[type] = value;
  if (type === "name") {
    globals.selectedFeature.popup.setContentHTML("<p>"+value+"</p>");
    globals.selectedFeature.attributes["name"] = value;
  }
  $.ajax({
    url: globals.urls.edit.replace("1", globals.selectedFeature.attributes.id),
    type: "post",
    data: d,
    success: function(req) {
      if (req.success === true) {
        alert_msg(gettext("Updated!"), "success");
      }
      else {
        alert_msg(gettext("Error :("), "error");
      }
      $("#updated_by").text(globals.username);
    }
  });
  return display_msg;
}

function save_timetable_edit(value, settings) {
  var display_msg = $(this).find("option[value='"+value+"']").text() || value;
  var weekday = $(this).parent().attr("wd");
  var index = $(this).parent().attr("index");
  var type = $(this).parent().attr("type");
  var n_fields = $(this).closest("tr").find("td").length;

  if (!index) {
    index = n_fields - 1;  // set index
    $(this).parent().attr("index", index);
  }

  var needs_new_input = true;
  $(this).closest("tr").find(".edit").each(function() {
    if ($(this).attr("index") === undefined) {
      needs_new_input = false;
    }
  });

  if (!value || value === "__:__") {
    needs_new_input = false;
    value = "";
    $(this).closest("td").remove();
  }

  // add another field
  if (needs_new_input) {
    var new_input = $("<td/>").append(
      $("<span/>").addClass("edit")
                  .attr("wd", weekday)
                  .attr("type", "opening")
        .append(
          $("<span/>").addClass("editable_time")
        )
    );
    new_input.append($("<span/>").text(" - "))
    new_input.append(
      $("<span/>").addClass("edit")
                  .attr("wd", weekday)
                  .attr("type", "closing")
        .append(
          $("<span/>").addClass("editable_time")
        )
    );
    $(this).closest("tr").append(new_input);
    new_input.find('.editable_time').editable(save_timetable_edit, {
      style: "inherit",
      type: "masked",
      mask: "99:99",
      placeholder: "00:00"
    });
  }

  var d = {weekday: weekday,
           optime: index}
  d[type] = value;  // type = opening or closing

  var that = this;
  $.ajax({
    url: globals.urls.edit.replace("1", globals.selectedFeature.attributes.id),
    type: "post",
    data: d,
    success: function(req) {
      if (req.success === true) {
        alert_msg(gettext("Updated!"), "success");
      }
      else {
        alert_msg(gettext("Error :("), "error");
        console.log(that);
        $(that).text("00:00");
      }
      $("#updated_by").text(globals.username);
    }
  });
  return display_msg;
}

function save_manytomany_edit(sing, plur) {
  return function(value, settings) {
    var data = [];
    if (value === "") {
      $(this).parent().remove();
    }
    else {
      data.push(value);
    }
    $(".editable_"+sing).each(function() {
      if ($(this).text() === gettext("Click to add")) {
        $(this).parent().remove();
      }
      else {
        if (!$(this).html().match("<form")) {
          if ($(this).text()) {
            data.push($(this).text());
          }
        }
      }
    });
    $.ajax({
      url: globals.urls.edit.replace("1", globals.selectedFeature.attributes.id),
      type: "post",
      data: plur+"[]="+data.join("&"+plur+"[]="),
      success: function(req) {
        if (req.success === true) {
          alert_msg(gettext("Updated!"), "success");
        }
        else {
          alert_msg(gettext("Error :("), "error");
        }
        $("#updated_by").text(globals.username);
      }
    });

    var new_input = $("<span/>").addClass("edit").append(
      $("<span/>").addClass("editable_"+sing)
    );
    $("#"+plur+"_info").append(new_input);
    manytomany_editable(".editable_"+sing, sing, plur);

    return value;
  }
}

function manytomany_editable(expr, sing, plur) {
  $(expr).editable(save_manytomany_edit(sing, plur), {
    submit: gettext("Save"),
    cancel: gettext("Cancel"),
    style: "inherit",
    type: "manytomany",
    onblur: "submit",
    placeholder: gettext("Click to add"),
    autocomplete: {
      source: function(request, response) {
        $.ajax({
          url: globals.urls.editdata.replace("1", sing),
          data: {
            q: request.term
          },
          success: function(data) {
            response($.map(data.results, function(item) {
              return {
                label: item.name,
                value: item.name
              }
            }));
          }
        });
      },
    }
  });
}
