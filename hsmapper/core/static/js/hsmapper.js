$.ajaxSetup({
  beforeSend: function(xhr, settings) {
      function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }
      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
          // Only send the token to relative URLs i.e. locally.
          xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
  },
  error: function() {
    alert_msg(gettext("Error! Request failed"));
  }
});

function init() {
  map = new OpenLayers.Map({
    div: "map",
    allOverlays: true,
    projection: new OpenLayers.Projection("EPSG:900913"),
    controls: [new OpenLayers.Control.Navigation(),
               new OpenLayers.Control.PanZoomBar()],
    numZoomLevels: 8
  });

  var heatmap_bounds = new OpenLayers.Bounds(-8083703.41947, 2179564.8117,
                                             -8043582.32418, 2211201.70086);
  heatmap_layer = new OpenLayers.Layer.WMS(
    "Hospitals Heatmap",
    "http://"+globals.server_ip+":"+globals.geoserver_port+"/geoserver/findmyspot/wms",
    {
        LAYERS: 'findmyspot:big_distance',
        STYLES: '',
        format: "image/png",
        tiled: true,
        tilesOrigin : heatmap_bounds.left + ',' + heatmap_bounds.bottom,
        transparent: true
    },
    {
        buffer: 0,
        displayOutsideMaxExtent: true,
        isBaseLayer: false
    });

  var osm = new OpenLayers.Layer.OSM("OSM",
      "http://tile.openstreetmap.org/${z}/${x}/${y}.png",
      {sphericalMercator: true, isBaseLayer:true});

  var clusterStyle = new OpenLayers.Style(
    {
      graphicName: "circle",
      strokeColor: "#ff0000",
      fillColor: "#ff0000",
      pointRadius: "${radius}",
      fillOpacity: 0.5,
      strokeWidth: "${width}"
    },
    {
      context: {
        radius: function(feature) {
          if (feature.attributes.count == 1) return 5;
          return Math.min(Math.ceil(feature.attributes.count / 5), 25) + 5;
        },
        width: function(feature) {
          return (feature.attributes.count > 1) ? 3 : 1;
        }
      }
    }
  );

  globals.hospital_layer = new OpenLayers.Layer.Vector(
       "Health facilities",
      {styleMap: clusterStyle,
       projection: new OpenLayers.Projection("EPSG:"+globals.srid),
       strategies: [new OpenLayers.Strategy.Fixed(),
                    new OpenLayers.Strategy.Cluster()],
       protocol: new OpenLayers.Protocol.HTTP({
          url: globals.urls.get,
          format: new OpenLayers.Format.GeoJSON()
       })
      }
  );

  globals.hospital_layer.events.register("featuresadded", globals.hospital_layer,
    function() {
      var extent = globals.hospital_layer.getDataExtent();
      if (!globals.featuresAdded) {
        map.zoomToExtent(extent);
      }
      globals.featuresAdded = true
    }
  );

  map.addLayers([osm, globals.hospital_layer]);
  map.zoomToMaxExtent();

  globals.selectControl = new OpenLayers.Control.SelectFeature(
    [globals.hospital_layer],
    {clickout: true, toggle: false, multiple: false, hover: false }
  );
  map.addControl(globals.selectControl);
  globals.selectControl.activate();

  globals.hospital_layer.events.on({
    "featureselected": function(e) {
      onFeatureSelect(e.feature);
    },
    "featureunselected": function(e) {
      onFeatureUnselect(e.feature);
    }
  });
  map.addControl(new OpenLayers.Control.MousePosition());

/*  globals.hospital_layer.events.register("refresh", globals.hospital_layer,
    function() {
      if (globals.selectedFeature) {
        globals.selectControl.unselect(globals.selectedFeature);
      }
    }
  );*/

  map.events.register("click", map, function(e) {
    if (globals.insert_mode) {
      if (globals.selectedFeature) {
        globals.selectControl.unselect(globals.selectedFeature);
      }
      var p = map.getLonLatFromPixel(e.xy);
      var point = new OpenLayers.Geometry.Point(p["lon"], p["lat"]);
      var f = new OpenLayers.Feature.Vector(point);
      globals.hospital_layer.addFeatures([f]);

      $.ajax({
        url: globals.urls.add,
        type: "post",
        data: {lat: p["lat"], lon: p["lon"]},
        success: function(req) {
          if (req.success === true) {
            alert_msg(gettext("Point inserted"), "success");
            f.attributes["id"] = req.id;
            onFeatureSelect(f, true);
          }
          else {
            alert_msg(gettext("Error :("));
          }
        }
      });
      toggle_insert();
    }
  });

  var DblclickFeature = OpenLayers.Class(OpenLayers.Control, {
    initialize: function (layer, options) {
      OpenLayers.Control.prototype.initialize.apply(this, [options]);
      this.handler = new OpenLayers.Handler.Feature(this, layer, {
        dblclick: this.dblclick,
        click: this.click
      });
    }
  });
  var dblclick = new DblclickFeature(globals.hospital_layer, {
    dblclick: function(event) {
      var point = event.geometry;
      map.zoomToExtent(point.bounds);
    },
    click: function(event) {
      onFeatureSelect(event);
    }
  });
//  map.addControl(dblclick);
//  dblclick.activate();

  layers = map.layers;
  for (var i=0; i<layers.length; i++) {
    if (layers[i].name.indexOf("OpenLayers.") == -1) {
      $(".multiselect").append($("<option></option>").
                        attr("value", layers[i].name).
                        attr("id", layers[i].id).
                        attr("selected", true).
                        text(layers[i].name));
    }
  }
  $(".multiselect").multiselect({
    sortable: 'left',
    sortableUpdate:
      function(event, ui, sortable) {
        var layer_list = sortable.sortable("toArray");
        var layer_id = ui.item.attr("id");
        var layer = map.getLayersBy("id", layer_id)[0];
        if (!(layer.isBaseLayer || layer_id.search("OSM") != -1)) {
          var layer_pos = layer_list.length - 1 - layer_list.indexOf(layer_id);
          if (layer_pos != 0) {
            console.log("moving " + layer_id + " to " + layer_pos);
            map.setLayerIndex(layer, layer_pos);
            return;
          }
        }
        sortable.sortable('cancel');
      },
    selected:
      function(event, ui) {
        map.getLayersByName($(ui.option).val())[0].setVisibility(true);
      },
    deselected:
      function(event, ui) {
        map.getLayersByName($(ui.option).val())[0].setVisibility(false);
      }
  });
  $.nominatim("#autocomplete", {select: function(item) {
    var bb = item.boundingbox;
    bb = new OpenLayers.Bounds(bb[2], bb[0], bb[3], bb[1]);
    bb = bb.transform(new OpenLayers.Projection('EPSG:4326'), new OpenLayers.Projection('EPSG:900913'));
    map.zoomToExtent(bb);
  }});
}

function onPopupClose(evt) {
  globals.selectControl.unselect(globals.selectedFeature);
}

function onFeatureSelect(feature, not_expired) {
  if (globals.selectedFeature) {
    globals.selectControl.unselect(globals.selectedFeature);
  }
  if (globals.delete_mode) {
    var agree = confirm(gettext("Are you sure you want to delete?"));
    if (agree) {
      globals.hospital_layer.removeFeatures([feature]);
      globals.selectedFeature = undefined;
      $.ajax({
        url: globals.urls.delete.replace("1", feature.attributes.id),
        type: "post",
        data: "",
        success: function(req) {
          if (req.success === true) {
            alert_msg(gettext("Deleted"), "success");
          }
          else {
            alert_msg(gettext("Error :("), "error");
          }
        }
      });
    }
    toggle_delete();
  }
  else {
    globals.selectedFeature = feature;
    var msg = "";

    if (feature.cluster) {
      var points_list = $("<ul/>");

      for (var i=0; i<feature.cluster.length; i++) {
        var f = feature.cluster[i];
        var name = f.attributes["name"] || gettext("No name");
        var click_callback = function(f) {
          return function() {
            f.layer = globals.hospital_layer
            globals.selectControl.unselect(globals.selectedFeature);
            globals.selectControl.select(f);
            return false;
          }
        }
        points_list.append(
          $("<li/>").append(
            $("<a/>").text(name).click(click_callback(f))
          )
        );
        msg += "<p>" + name + "</p>";
      }

      var points = $("<div/>").append(points_list);
      $("#edit_info").empty().append(points_list);
    }
    else {
      var name = feature.attributes["name"] || gettext("No name")
      msg += "<p>" + name + "</p>";
    }

    var desc = $("<div/>");
    desc.html(msg);

    popup = new OpenLayers.Popup.FramedCloud("chicken",
                feature.geometry.getBounds().getCenterLonLat(),
                new OpenLayers.Size(1500,1000),
                desc.html(),
                null,
                true,
                onPopupClose);
    feature.popup = popup;
    map.addPopup(popup);

    if (!feature.cluster) {
      get_hospital_data(not_expired);
    }
  }
}

function get_hospital_data(not_expired) {
  $.get(globals.urls.info.replace("1", globals.selectedFeature.attributes.id), function(data) {
    $("#edit_info").html(data);
    if (not_expired) {
      $(".expired").removeClass("expired");
      $("#expired_alert").remove();
    }
    if (globals.username) {
    $('.editable').editable(save_feature_edit, {
      submit: gettext("Save"),
      cancel: gettext("Cancel"),
      style: "inherit",
      width: 180,
      placeholder: gettext("Click to edit")
    });
    $('.editable_text').editable(save_feature_edit, {
      submit: gettext("Save"),
      cancel: gettext("Cancel"),
      style: "inherit",
      type: "autogrow",
      rows: 5,
      cols: 40,
      placeholder: gettext("Click to edit")
    });
    $('.editable_type').editable(save_feature_edit, {
      submit: gettext("Save"),
      cancel: gettext("Cancel"),
      style: "inherit",
      loadurl: globals.urls.editdata.replace("1", "type"),
      type: "select",
      placeholder: gettext("Click to edit")
    });
    $('.editable_date').editable(save_feature_edit, {
      submit: gettext("Save"),
      cancel: gettext("Cancel"),
      style: "inherit",
      type: "masked",
      mask: "99/99/9999",
      placeholder: gettext("Click to edit")
    });
    $('.editable_time').editable(save_timetable_edit, {
      style: "inherit",
      type: "masked",
      mask: "99:99",
      placeholder: "00:00"
    });
    $('.editable_manager').editable(save_feature_edit, {
      submit: gettext("Save"),
      cancel: gettext("Cancel"),
      style: "inherit",
      loadurl: globals.urls.editdata.replace("1", "manager"),
      type: "select",
      placeholder: gettext("Click to edit")
    });
    $('.editable_checkbox').editable(save_feature_edit, {
      submit: gettext("Save"),
      cancel: gettext("Cancel"),
      style: "inherit",
      type: "checkbox",
      checkbox: {trueValue: gettext('Yes'),
                 falseValue: gettext('No')},
      placeholder: gettext("Click to edit")
    });

    manytomany_editable(".editable_pathology", "pathology", "pathologies");
    manytomany_editable(".editable_service", "service", "services");
  }
  else {
    $(".edit").removeClass("edit");
  }
  });
}

function onFeatureUnselect(feature) {
  if (feature.popup) {
    map.removePopup(feature.popup);
    feature.popup.destroy();
    feature.popup = undefined;
  }
  globals.selectedFeature = undefined;
  $("#edit_info").empty();
}

function toggle_insert() {
  if (globals.delete_mode) {
    toggle_delete();
  }
  if (globals.insert_mode) {
    $("#insert_button").removeClass("success");
    $("#map").removeClass("crosshair");
    globals.insert_mode = false;
  }
  else {
    $("#insert_button").addClass("success");
    $("#map").addClass("crosshair");
    globals.insert_mode = true;
    if (globals.selectedFeature) {
      globals.selectControl.unselect(globals.selectedFeature);
    }
  }
}

function toggle_delete() {
  if (globals.insert_mode) {
    toggle_insert();
  }
  if (globals.delete_mode) {
    $("#delete_button").removeClass("success");
    $("#map").removeClass("crosshair");
    globals.delete_mode = false;
  }
  else {
    $("#delete_button").addClass("success");
    $("#map").addClass("crosshair");
    globals.delete_mode = true;
    if (globals.selectedFeature) {
      globals.selectControl.unselect(globals.selectedFeature);
    }
  }
}

function alert_msg(msg, level) {
  level = level || "error";
  $("#alert_box").fadeOut(300, function() {
    if (globals.close_timeout) {
      clearTimeout(globals.close_timeout);
    }
    $("#alert_box").fadeIn(300);
    $("#alert_box .alert-message").removeClass("warning");
    $("#alert_box .alert-message").removeClass("info");
    $("#alert_box .alert-message").removeClass("error");
    $("#alert_box .alert-message").removeClass("success");
    $("#alert_box .alert-message").addClass(level);
    $("#alert_box .alert-message").addClass("in");
    $("#alert_msg").html(msg);
    globals.close_timeout = setTimeout("$('.close').click()", 5000);
  });
}
