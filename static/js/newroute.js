// Coded with ♥ by Juan-Pablo Scaletti (jpscaletti) & the amazing Worldrat team.
"use strict";

var KEY_DELETE = 8
var KEY_ENTER = 13;

var W = {};

$(document).ready(function () {
  $('#error').alert();
  W.geo.init();
  W.route.init();
  W.search.init();
});


/* #!Globals
 *******************************************************************************/

W.globals = {
  SEARCH_RADIUS: 50000, // meters
  SEARCH_LIMIT: 40,
  SEARCH_LOCALE: 'en',
  FOURSQUARE_CLIENT_ID: 'WW2TD5MTTF1B10WM0CPZJTCUYDONXPSWPPQZ0QEHXNSDA5VS',
  FOURSQUARE_CLIENT_SECRET: 'IYOLFXAEUDWJASJPWVUUPDXNI1EBZAWODZPBKE3IBTG1MCLA',
  DEFAULT_CAT_ID: '4e67e38e036454776db1fb3a', // Residences

  SEARCH_KEYDOWN_MINLEN: 1, // numchars
  SEARCH_KEYDOWN_WAIT: 400, // ms
  SEARCH_RESULTS_MAP_SIZE: [260, 260],
  SEARCH_RESULTS_ZOOM_LEVEL: 17,

  LAT: -12.1259255,
  LNG: -77.0289959,
  LATLNG_CITY_KEY: 'latlng_city',
  LATLNG_COORDS_KEY: 'latlng_coords',

  _: ''
};

W.error = function (msg) {
  $('#error div.error-body').html(msg);
  $('#error').slideDown();
};

W.storageSet = function (name, value) {
  if (!window.localStorage) {
    return;
  }
  localStorage.setItem(name, value);
  return value;
};

W.storageGet = function (name) {
  if (!window.localStorage) {
    return;
  }
  return localStorage.getItem(name);
};


/* #!Geo
 *******************************************************************************/
W.geo = {};

W.geo.init = function () {
  this.$cityInput = $('#city');
  this.restoreLocation();
  this.bindCitySearch();
};

W.geo.setLocation = function (latitude, longitude) {
  var $city = W.geo.$cityInput;
  var coords = [latitude, longitude].join(',');
  W.globals.LAT = latitude;
  W.globals.LNG = longitude;
  $city.attr('data-coords', coords);
  W.storageSet(W.globals.LATLNG_COORDS_KEY, coords);
  W.storageSet(W.globals.LATLNG_CITY_KEY, $city.val());
  // console.debug(coords);
};

W.geo.restoreLocation = function () {
  var $city = $('#city');
  var coords = W.storageGet(W.globals.LATLNG_COORDS_KEY);
  var city_name = W.storageGet(W.globals.LATLNG_CITY_KEY);
  if (coords) {
    $city.val(city_name);
    coords = coords.split(',');
    W.geo.setLocation(coords[0], coords[1]);
    return;
  }

  coords = $city.attr('data-coords').split(',');
  var DEFAULT_LAT = +coords[0];
  var DEFAULT_LNG = +coords[1];

  GMaps.geolocate({
    success: function (pos) {
      W.geo.setLocation(pos.coords.latitude, pos.coords.longitude);
    },
    error: function (error) {
      console.error(error.message);
      W.geo.setLocation(DEFAULT_LAT, DEFAULT_LNG);
    },
    not_supported: function () {
      // console.debug('Your browser does not support geolocation');
      W.geo.setLocation(DEFAULT_LAT, DEFAULT_LNG);
    }
  });
};

W.geo.bindCitySearch = function () {
  var $city = W.geo.$cityInput;
  if ($city.length === 0) {
    return;
  }

  var setDefault = function () {
      var val = $.trim($city.val());
      if (!val) {
        $city.val($city.attr('data-default') || '');
      }
    };

  $city.on('mousedown', function (e) {
    e.preventDefault();
    e.stopPropagation();
    $city[0].select();
    return false;
  });

  $city.on('keydown', function (e) {
    if (e.which == KEY_ENTER) {
      e.preventDefault();
      e.stopPropagation();
      W.search.$searchInput.trigger('keypress');
      return false;
    }
  });

  $(document).on('mousedown', function () {
    setDefault();
  });

  var options = {
    types: ['(cities)']
  };

  var onPlaceChange = function () {
    var place = autocomplete.getPlace();
    if (!place) {
      setDefault();
      return false;
    }
    var location = place.geometry.location;
    W.geo.setLocation(location.lat(), location.lng());
    W.search.$searchInput.trigger('keypress');
  };

  var autocomplete = new google.maps.places.Autocomplete($city[0], options);
  google.maps.event.addListener(autocomplete, 'place_changed', onPlaceChange);
};


/* #!Route
 *******************************************************************************/
W.route = {};

W.route.init = function () {
  var json = CIRCUIT_DATA_JS;
  json = json.replace(/(\r\n|\n|\r)/gm,"");

  this.data = $.parseJSON(json);
  this.stops = {};

  this.tmpl_new_stop = $('#tmpl-new-stop').html();

  this.bindModals();
  this.initStops();
};

W.route.bindModals = function () {
  var $modal = $('#route-edit-modal');
  $modal.modal({
    show: false
  });
  W.route.$modal = $modal;

  $modal.find('.btn-primary').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    if (W.route.save()) {
      $modal.modal('hide');
    };
    return false;
  });

  var $deleteRouteForm = $('._delete-route-form');
  $deleteRouteForm.on('submit', function(e) {
    if (!confirm($deleteRouteForm.attr('data-msg'))){
      e.preventDefault();
      return false;
    };
  });

  $('._route-edit-trigger').click(function (e) {
    W.route.edit();
  });

  var $modalPicture = $('#route-picture-edit-modal');
  W.route.$modalPicture = $modalPicture;
  W.route.picIframe = $('iframe[name="' + $modalPicture.attr('target') + '"]')[0];

  $('._route-pic-trigger').on('click', function (e) {
    W.route.editPicture();
  });
};

W.route.edit = function () {
  var $modal = W.route.$modal;
  var data = W.route.data;

  $modal.find('[name=name]').val(data.name);
  $modal.find('[name=category]').val(data.category);
  $modal.find('[name=description]').val(data.description);
  $modal.find('[name=adult_content]').val(data.adult_content);
  $modal.modal('show');
};

W.route.save = function () {
  var $modal = W.route.$modal;
  var data = W.route.data;
  var params = {};

  var $nameInput = $modal.find('[name=name]');
  if (!$.trim($nameInput.val())) {
    $nameInput.focus().shakeIt();
    return false;
  }

  params.circuit_id = data.id;
  params.name = $nameInput.val();
  params.category = $modal.find('[name=category]').val();
  params.description = $modal.find('[name=description]').val();
  //params.adult_content = $modal.find('[name=adult_content]').val();
  if($modal.find('input[name=adult_content]').is(':checked')){
    params.adult_content = true;
  }else{
    params.adult_content = false;
  }

  var $cats = $modal.find('[name=category]');

  data.name = params.name;
  data.category = $cats.val();
  data.category_display = $cats.find('option:selected').text();
  data.description = params.description;
  data.adult_content = params.adult_content;
  W.route.data = data;

  $('.route-title').text(data.name);
  $('.category-display').text(data.category_display);
  $('.route-description').text(data.description);
  $('input[name=adult_content]').attr('value', params.adult_content);

  $.ajax({
    type: 'POST',
    url: CIRCUIT_EDIT_URL,
    data: params,
    error: function (jqXHR, textStatus, errorThrown) {
      // console.info(textStatus);
      console.error(errorThrown);
    }
  });

  $('#route-stops').data('colset').update(true);
  return true;
};

W.route.editPicture = function () {
  var $modal = W.route.$modalPicture;
  var data = W.route.data;
  var $routePic = $('.route-main-pic');
  var iframe = W.route.picIframe;

  $modal.find('img').attr('src', data.picture_url);
  $modal.modal('show');

  iframe.contentWindow.document.innerHTML = '';
  iframe.removeAttribute('src');

  $modal.unbind('submit').submit(function () {
    $routePic.addClass('wait');
    $modal.modal('hide');
  });

  iframe.onload = function () {
    $routePic.removeClass('wait');

    var $response = $(iframe.contentWindow.document.body);
    var new_data;
    try {
      new_data = $.parseJSON($response.text());
    } catch (e) {
      new_data = null;
    }

    if (!new_data || new_data.error) {
      var msg = new_data ? new_data.error : $response.html();
      W.error(msg);
      return;
    }

    W.route.data.picture_url = new_data.picture_url;
    var $img = $routePic.find('img');
    if ($img.length === 0){
      $img = $('<img />').prependTo($routePic);
    }
    $img.attr('src', new_data.picture_url)
      .attr('data-ratio-hw', new_data.picture_ratio_hw);
    var $stops = $('#route-stops');
    $stops.find('._route-pic-trigger').hide();
    $stops.data('colset').update(true);
  };
};

W.route.initStops = function () {
  var $routeStops = $('#route-stops');
  var stops = {};

  $routeStops.find('._stop').each(function () {
    var stop = new W.Stop(this);
    stops[stop.data.place_id] = stop;
  });
  W.route.stops = stops;

  $routeStops.on('click', '.stop-edit', function (e) {
    var id = this.getAttribute('data-id');
    var stop = W.route.stops[id];
    if (!stop) {
      console.error('Missing place_id=' + id);
      return;
    }
    stop.edit();
  });

  var $modal = $('#stop-edit-modal');
  $modal.modal({
    show: false
  });

  W.Stop.prototype.$modal = $modal;
  W.Stop.prototype.iframe = $('iframe[name="' + $modal.attr('target') + '"]')[0];

  $modal.find('button.stop-remove').on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var $a = $(this);
    var msg = $a.attr('data-msg');
    if (msg && !confirm(msg)) {
      return false;
    }
    $modal.data('stop').remove();
    $modal.modal('hide');
    return false;
  });
};

W.route.addStop = function (data) {
  var $r = $(W.route.tmpl_new_stop);
  var picture = data.picture_url;
  if (picture) {
    $r.find('img').attr('src', picture);
  } else {
    $r.find('img').remove();
  }
  $r.find('.stop-type').text(data.place_type);
  $r.find('.stop-name').text(data.name);
  $r.find('.stop-address').text(data.address);
  $r.find('.stop-description').text(data.description);
  $r.find('.stop-edit').attr('data-id', data.place_id);

  var $colSet = $('#route-stops');
  // Update column set
  $r.insertAfter($colSet.find('._sticky:last'));
  $colSet.data('colset').update(true);

  $r.find('.item-options .btn').tooltip();
  var stop = new W.Stop($r, data);
  W.route.stops[data.place_id] = stop;
};


W.route.removeStop = function (stop) {
  delete W.route.stops[stop.data.place_id];
  $('#route-stops').data('colset').u(true);
};


/* #!Stops
 *******************************************************************************/
W.Stop = function (stop, data) {
  this.$stop = $(stop);
  if (!data) {
    var json = $('<div/>').html(this.$stop.attr('data-json')).text();
    data = $.parseJSON(json);
    this.$stop.removeAttr('data-json');
  }
  this.data = data;
};

W.Stop.prototype.edit = function () {
  var stop = this;
  var $modal = stop.$modal;
  var data = stop.data;
  $modal.data('stop', stop);

  $modal.attr('action', data.update_url);
  $modal.find('.stop-delete').attr('href', data.delete_url);

  $modal.find('.stop-name').text(data.name);
  $modal.find('.cat').text(data.place_type);
  $modal.find('.stop-address').text(data.address);
  $modal.find('img').attr('src', data.picture_url);
  $modal.find('[name=description]').val(data.description);
  $modal.find('[name=stop_id]').val(data.place_id);
  $modal.modal('show');

  stop.iframe.contentWindow.document.innerHTML = '';
  stop.iframe.removeAttribute('src');

  $modal.unbind('submit').submit(function () {
    stop.$stop.addClass('wait');
    $modal.modal('hide');
  });

  stop.iframe.onload = function () {
    stop.$stop.removeClass('wait');

    var $response = $(stop.iframe.contentWindow.document.body);
    var new_data;
    try {
      new_data = $.parseJSON($response.text());
    } catch (e) {
      new_data = null;
    }

    if (!new_data || new_data.error) {
      var msg = new_data ? new_data.error : $response.html();
      W.error(msg);
      return;
    }
    stop.update(new_data);
  };
};

W.Stop.prototype.remove = function () {
  var stop = this;
  $.ajax({
    type: 'POST',
    url: stop.data.delete_url,
    success: function () {
      var $stop = stop.$stop;
      $stop.animate(
        {
          opacity: 0
        },
        function () {
          $stop.remove();
          $('#route-stops').data('colset').update(true);
        }
      );
      W.route.removeStop(stop);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      // console.info(textStatus);
      console.error(errorThrown);
    }
  });
};

W.Stop.prototype.update = function (data) {
  var $stop = this.$stop;
  $stop.find('.stop-name').text(data.name);
  $stop.find('.stop-address').text(data.address);
  $stop.find('.stop-description').text(data.description);
  $stop.find('._stop-thumbnail')
    .attr('src', data.picture_url)
    .attr('data-ratio-hw', data.picture_ratio_hw);
  this.data = data;
  setTimeout(function(){
    $('#route-stops').data('colset').update(true);
  }, 500);
};


/* #!Search
 *******************************************************************************/
W.search = {
  SEARCH_URL: 'https://api.foursquare.com/v2/venues/search'
};

W.search.init = function () {
  this.$results = $('#search-results');
  this.$noResults = $('#no-results').hide();
  this.$newPlaceBtn = $('#add-new-place-btn').hide();
  this.$searchInput = $('#query');
  this.bindModal();
  this.bindSearch();
  this.bindNewPlaceModal();
};

W.search.bindModal = function () {
  var $modal = $('#stop-new-modal');
  $modal.modal({
    show: false
  });
  this.$modal = $modal;
  this.iframe = $('iframe[name="' + $modal.attr('target') + '"]')[0];

  this.$results.on('click', '._search-result', function (e) {
    var data = $(this).data('data');
    W.search.addStop(data);
  })
};

W.search.bindSearch = function () {
  this.tmpl_search_result = $('#tmpl-search-result').html();
  var $results = this.$results.empty();
  this.$results = $results;

  var timeoutId;
  var $cityInput = W.geo.$cityInput;
  var $searchInput = this.$searchInput;
  var $searchTitle = $('#results-title');
  var $searchTitleTerm = $('#results-title .search-term');
  var $searchTitleLocation = $('#results-title .search-location');

  function search() {
    if ($searchInput.val().length < W.globals.SEARCH_KEYDOWN_MINLEN){
      $results.empty().removeClass('wait').hide();
      $searchTitle.hide();
      return;
    }
    
    $searchTitleTerm.text($searchInput.val());
    $searchTitleLocation.text($cityInput.val());
    $searchTitle.fadeIn();

    var request = {
      ll: W.globals.LAT + ',' + W.globals.LNG,
      intent: 'browse',
      query: $searchInput.val(),
      radius: W.globals.SEARCH_RADIUS,
      locale: W.globals.SEARCH_LOCALE,
      limit: W.globals.SEARCH_LIMIT,
      client_id: W.globals.FOURSQUARE_CLIENT_ID,
      client_secret: W.globals.FOURSQUARE_CLIENT_SECRET,
      v: '20120530'
    };
    W.search.FoursquareSearch(request);
  }

  function preSearch(){
    clearTimeout(timeoutId);
    $results.empty().removeClass('wait').hide();
    $searchTitle.hide();
    if ($searchInput.val().length < W.globals.SEARCH_KEYDOWN_MINLEN) {
      return;
    }
    W.search.$noResults.hide();
    W.search.$newPlaceBtn.hide();
    $results.show().addClass('wait');

    timeoutId = setTimeout(search, W.globals.SEARCH_KEYDOWN_WAIT);
  }

  $searchInput.keypress(preSearch);
  $searchInput.keydown(function(e){
    if (e.which === KEY_DELETE){
      preSearch();
    }
  });
};

W.search.FoursquareSearch = function (request) {
  this.$results.css('height', 'auto').show().addClass('wait');

  var onSuccess = function (resp, status, jqXHR) {
      W.search.$results.removeClass('wait').empty();
      var i, venue, data;
      var venues = resp.response.venues;
      for (i = 0; venue = venues[i]; i++) {
        data = W.search.normalizeFoursquareData(venue);
        if (W.route.stops[venue.id]) {
          continue;
        }
        W.search.showSearchResult(data);
      }
      if (W.search.$results.find('article').length == 0) {
        W.search.$noResults.show();
      }

      // Update column set
      W.search.$results.data('colset').update(true);
      W.search.$newPlaceBtn.show();
    };

  var onError = function (jqXHR, status, error) {
      W.search.$results.removeClass('wait');
      console.error(error);
    };

  $.ajax({
    url: W.search.SEARCH_URL,
    data: request,
    dataType: 'json',
    success: onSuccess,
    error: onError
  });
};

W.search.normalizeFoursquareData = function (data) {
  var categories = [];
  var i, cat;
  for (i = 0; cat = data.categories[i]; i++) {
    categories.push(cat.id);
  }

  return {
    place_id: data.id,
    name: data.name,
    address: data.location.address,
    crossStreet: data.location.crossStreet,
    city: data.location.city,
    state: data.location.state,
    country: data.location.country,
    lat: data.location.lat,
    lng: data.location.lng,
    place_type: data.categories[0] ? data.categories[0].shortName : '-',
    // categories: categories.join(','),
    place_type_id: categories[0] || W.globals.DEFAULT_CAT_ID,
    phone: data.contact.phone,
    twitter: data.contact.twitter,
    website: data.url
  }
};

W.search.showSearchResult = function (data) {
  var $r = $(W.search.tmpl_search_result);
  $r.find('.stop-type').text(data.stop_type);
  $r.find('.stop-name').text(data.name);
  $r.find('.stop-address').text(data.address);
  $r.find('.stop-cross-street').text(data.crossStreet);
  var $img = $r.find('img')
  var mapURL = W.search.makeStaticMapURL(data.lat, data.lng);
  $img.attr('src', mapURL);
  $img.attr('alt', data.name);
  $r.appendTo(W.search.$results);
  
  $r.data('data', data);
};

W.search.makeStaticMapURL = function (lat, lng) {
  return GMaps.staticMapURL({
    url: STATIC_MAPS_ROOT,
    size: W.globals.SEARCH_RESULTS_MAP_SIZE,
    zoom: W.globals.SEARCH_RESULTS_ZOOM_LEVEL,
    key: GOOGLE_API_KEY,
    marker: {lat: lat, lng: lng}
  });
};

W.search.addStop = function (data) {
  var $modal = W.search.$modal;
  var $stops = $('#route-stops');

  $modal.find('.stop-name').text(data.name || '');
  $modal.find('.cat').text(data.place_type || '');
  $modal.find('.stop-address').text(data.address || '');
  $modal.find('.stop-cross-street').text(data.crossStreet || '');

  var $input;
  $.each(data, function (key, value) {
    $input = $modal.find('[name=' + key + ']');
    if ($input.length) {
      $input.val(value);
    }
  });

  $modal.find('[name=description]').val('');
  $modal.modal('show');

  W.search.iframe.contentWindow.document.innerHTML = '';
  W.search.iframe.removeAttribute('src');

  $modal.unbind('submit').submit(function () {
    W.search.$results.empty().css('height', 'auto');
    W.search.$newPlaceBtn.hide();
    $('#query').val('');

    $stops.addClass('wait');
    $modal.modal('hide');
  });

  W.search.iframe.onload = function () {
    $stops.removeClass('wait');
    var $response = $(W.search.iframe.contentWindow.document.body);
    var new_data;
    try {
      new_data = $.parseJSON($response.text());
    } catch (e) {
      new_data = null;
    }

    if (!new_data || new_data.error) {
      var error = new_data ? new_data.error : $response.html();
      $('#error').slideDown().find('div.error-body').html(error);
      return;
    }

    new_data.o = data;
    new_data = W.search.normalizeNewStopData(new_data);
    W.route.addStop(new_data);
  };
};

W.search.normalizeNewStopData = function (data) {
  var stop = data.circuit_stop;
  var place = stop.place;

  var picture_url = stop.picture.thumbnails.squared;
  if (!picture_url) {
    picture_url = W.search.makeStaticMapURL(place.coordinates.lat, place.coordinates.lng);
  }
  var description = stop.description;
  if (description === 'None') {
    description = '';
  }
  var place_type = (place.place_type && place.place_type.short_name) || '';

  return {
    place_id: data.o.place_id,
    name: place.name,
    picture_url: picture_url,
    description: description,
    address: place.address,
    place_type_id: place.place_type_id || W.globals.DEFAULT_CAT_ID,
    place_type: place_type,
    update_url: stop.update_url,
    _: ''
  };
};

W.search.bindNewPlaceModal = function () {
  var $placeTypeSelect = $('#new-place-type');

  function formatPlaceType(pt) {
    return '<img class="place_type_img" src="' + $placeTypeSelect.find('[value="' + pt.id + '"]').attr('data-icon') + '"/>' + pt.text;
  }
  $placeTypeSelect.select2({
    formatResult: formatPlaceType,
    formatSelection: formatPlaceType
  });

  var $modal = $('#new-place-modal');
  var $name = $('#new-place-name');
  var $placeTypeSelect = $('#new-place-type');
  var $search = $('#new-place-search');
  var $searchBtn = $('#new-place-search-btn');
  var map, marker, markerPos;

  $modal.modal({
    show: false
  });

  W.search.$newPlaceBtn.on('click', function (e) {
    e.preventDefault();
    e.stopPropagation();
    $name.val('');
    $search.val('');
    $modal.modal('show');
    return false;
  });

  $modal.on('shown', function () {
    markerPos = markerPos || [W.globals.LAT, W.globals.LNG];

    map = new GMaps({
      div: '#new-place-map',
      zoom: 16,
      lat: markerPos[0],
      lng: markerPos[1],
      click: function (ev) {
        markerPos = [ev.latLng.lat(), ev.latLng.lng()];
        marker.setPosition(ev.latLng);
      }
    });

    marker = map.addMarker({
      lat: markerPos[0],
      lng: markerPos[1]
    });

    var geolocate = function (callback) {
        GMaps.geolocate({
          success: function (position) {
            markerPos = [position.coords.latitude, position.coords.longitude];
            map.setCenter(markerPos[0], markerPos[1]);
            if (callback) {
              callback(markerPos);
            }
          }
        });
      };

    geolocate(function (markerPos) {
      var latLng = new google.maps.LatLng(markerPos[0], markerPos[1]);
      marker.setPosition(latLng);
    });

    map.addControl({
      position: 'top_right',
      text: 'Geolocate',
      style: {
        margin: '5px',
        padding: '1px 6px',
        border: 'solid 1px #717B87',
        background: '#fff'
      },
      events: {
        click: geolocate
      }
    });

    $searchBtn.unbind().on('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      GMaps.geocode({
        address: $search.val(),
        callback: function (results, status) {
          if (status == 'OK') {
            marker.setMap(null);
            var latLng = results[0].geometry.location;
            markerPos = [latLng.lat(), latLng.lng()];
            map.setCenter(markerPos[0], markerPos[1]);
            marker = map.addMarker({
              lat: markerPos[0],
              lng: markerPos[1]
            });
          }
        }
      });
      return false;
    });

  }); //$modal.on('shown', function(){

  $search.on('keydown', function (e) {
    if (e.which == KEY_ENTER) {
      e.preventDefault();
      e.stopPropagation();
      $searchBtn.trigger('click');
      return false;
    }
  });

  $name.on('keydown', function (e) {
    if (e.which == KEY_ENTER) {
      e.preventDefault();
      e.stopPropagation();
      return false;
    }
  });

  $modal.submit(function (e) {
    e.preventDefault();
    e.stopPropagation();
    var name = $.trim($name.val());
    if (!name) {
      $name.focus().shakeIt();
      return false;
    }
    W.search.addStop({
      name: name,
      place_type_id: $placeTypeSelect.val(),
      lat: markerPos[0],
      lng: markerPos[1]
    });
    $modal.modal('hide');
    return false;
  });
};
