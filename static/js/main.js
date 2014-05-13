"use strict";

var KEY_ENTER = 13;
var KEY_TAB = 9;

$(document).ready(function () {
   $('#welcomeCarousel').carousel({interval:5000});
   columnize();
   bindActions();
   calcDistances();
   bindWidgets();
   bindShare();
   bindCitySearch();
   bindLoadMore();
   bindRemix();
   bindAccountSettings();
   $('#load-more').css('display', 'block').show();
});


function storageSet(name, value) {
  if (!window.localStorage) {
    return;
  }
  localStorage.setItem(name, value);
  return value;
}


function storageGet(name) {
  if (!window.localStorage) {
    return;
  }
  return localStorage.getItem(name);
}


function ColSet(section, sorted) {
   this.PADDING = 36;

   this.$section = $(section).css('position', 'relative');
   this.getLimits();
   var self = this;
   var tx1, tx2, tx3;
   var isIE = (navigator.appName == 'Microsoft Internet Explorer');

   var onResize = function () {
      if (isIE){
         window.onresize = null;
         self.update(sorted);
         setTimeout(function(){
            window.onresize = onResize;
         }, 10);
         return false;
      }
      
      clearTimeout(tx1);
      clearTimeout(tx2);
      clearTimeout(tx3);

      tx1 = setTimeout(function(){
         self.update(sorted);
         tx2 = setTimeout(function(){
            self.update(sorted);
            tx3 = setTimeout(function(){
               self.update(sorted);
            }, 300);
         }, 300);
      }, 100);
   };

   onResize();
   window.onresize = onResize;
}


ColSet.prototype.getLimits = function () {
   /*
  :attr data-columns:
    Tuple of minimum and maximum width (in pixels) for a column. 
    Eg: "120,200".
    Columns will be created and removed automatically according to the
    width of the container, so the at any moment **less** columns are used.
  */
   var limits = this.$section.attr('data-columns').split(/\s*,\s*/);
   var min = parseInt(limits[0], 10);
   var max = parseInt(limits[1], 10);
   if (isNaN(max) || max < min) {
      max = min;
   }
   if (isNaN(min)) {
      console.error([min, max]);
      return;
   }
   this.min = min;
   this.max = max;
};

ColSet.prototype.getColWidth = function () {
   var w = this.$section.width();
   var numCols = Math.ceil(w / this.max);
   var colWidth = Math.floor(w / numCols);
   if (colWidth < this.min) {
      numCols -= 1;
      colWidth = Math.floor(w / numCols);
   }
   this.colWidth = colWidth;
   this.numCols = numCols;
};


ColSet.prototype.update = function (sorted) {
   if (sorted){
      this.sorted_update();
   } else {
      this.masonry_update();
   }
}


ColSet.prototype.sorted_update = function () {
   var $children = this.$section.children();
   var children = _.toArray($children);
   var numChildren = children.length;

   this.getColWidth();
   var colWidth = this.colWidth;
   var numCols = this.numCols;
   var x = 0;
   var y = [];

   var row, icol, item, $item, $img, ratio;

   for (row = 0; row < numChildren; row += numCols) {
      x = 0;

      for (icol = 0; icol < numCols; icol += 1) {
         item = children[row + icol];
         if (!item) {
            break;
         }
         $item = $(item);

         $img = $item.find('[data-ratio-hw]');
         ratio = parseInt($img.attr('data-ratio-hw'), 10) / 100;
         $img.css({
            width: (colWidth - this.PADDING) + 'px',
            height: ratio * (colWidth - this.PADDING) + 'px'
         });

         $item.css({
            top: (y[icol] || 0) + 'px',
            left: x + 'px',
            width: colWidth + 'px',
            visibility: 'visible',
            display: 'block'
         });

         x += colWidth;
         y[icol] = (y[icol] || 0) + $item.height();
      }
      this.$section.height(_.max(y));
   }

   this.y = y;
   this.$section.height(_.max(y));
};


ColSet.prototype.masonry_update = function () {
   var $section = this.$section;
   var $children = $section.children();
   var children = _.toArray($children);

   this.getColWidth();
   var colWidth = this.colWidth;
   var numCols = this.numCols;
   var PADDING = this.PADDING;

   var icol, item, $item, $img, ratio;

   var x = 0;
   var y = [];
   // The _.indexOf(y, _.min(yswill not work otherwise.
   for (icol=0; icol<numCols; icol++){
      y[icol] = 0;
   }

   _.each(children, function(item){
      $item = $(item);
      icol = _.indexOf(y, _.min(y));

      $img = $item.find('[data-ratio-hw]');
      ratio = parseInt($img.attr('data-ratio-hw'), 10) / 100;
      $img.css({
         width: (colWidth - PADDING) + 'px',
         height: ratio * (colWidth - PADDING) + 'px'
      });

      $item.css({
         top: (y[icol] || 0) + 'px',
         left: (icol * colWidth) + 'px',
         width: colWidth + 'px',
         visibility: 'visible',
         display: 'block'
      });

      y[icol] = (y[icol] || 0) + $item.height();
      $section.height(_.max(y));
   });

   this.y = y;
};


ColSet.prototype.append = function (item) {
   /** Append an item in the shorter column available.
   */
   var y = this.y;
   var colWidth = this.colWidth;
   var icol = _.indexOf(y, _.min(y));

   var $item = $(item);
   var $img = $item.find('[data-ratio-hw]');
   var ratio = parseInt($img.attr('data-ratio-hw'), 10) / 100;
   $img.css('height', ratio * (colWidth - this.PADDING) + 'px');

   $item.css({
      top: (y[icol] || 0) + 'px',
      left: (icol * colWidth) + 'px',
      width: colWidth + 'px',
      visibility: 'visible',
      display: 'block'
   });
   this.$section.append($item);

   y[icol] = (y[icol] || 0) + $item.height();
   this.$section.height(_.max(y));
   this.y = y;
};


function columnize() {
   $('[data-columns]').each(function (index, el) {
      var $el = $(el);
      var sorted = $el.is('[data-sorted]');
      $el.data('colset', new ColSet(el, sorted));
   });
}


function bindWidgets() {
   $('[placeholder]').placeholder();
   $('.no-touch .btn-tooltip').tooltip();
   $('.dropdown-toggle').dropdown();
   $('.styled-checks input').on('change', function(){
      $(this).parents('label').toggleClass('checked', $(this).is(':checked'));
   });
}


function bindShare() {
   $(document).on('click', '.social-sharing .btn', function (e) {
      e.preventDefault();
      var $btn = $(this);
      var $el = $btn.parents('.social-sharing');
      var type = $btn.attr('data-type');
      var url = $el.attr('data-url') || window.location.href;
      var message = $el.attr('data-message') || '';
      share(type, url, message);
   });

   $(document).on('click', '[data-embed]', function (e) {
      e.preventDefault();
      var url = $(this).attr('data-url') || window.location.href + 'embedform/';
      window.open(url, "embedform", "width=600, height=400");
   });
}

function share(type, url, message) {
   var shareTo = {
      facebook: facebookShare,
      twitter: twitterShare
   };
   shareTo[type](url, message);
}

function facebookShare(url, message) {
    var obj = {
        method: 'feed',
        link: window.location.href,
        picture: $('meta[property="og:image"]').attr('content') || 'http://dev.worldrat.com/static/images/logo/nu-green.png',
        name: $('meta[property="og:title"]').attr('content'),
        caption: $('meta[property="og:caption"]').attr('content'),
        description: $('meta[property="og:description"]').attr('content')
    };
    function callback(response) {
	console.log(response);
    }

    FB.ui(obj, callback);
}

function twitterShare(url, message) {
   var max_char = 140;
   var hashtag = '#worldrat';
   var message_max = max_char - url.length - hashtag.length - 3;
   if (message.length > message_max) {
      message = message.substr(0, message_max - 2);
      message += "…";
   }
   message = [message, url, hashtag].join(' ');

   var share_url = 'http://twitter.com/intent/tweet?text=' + encodeURIComponent(message);

   window.open(share_url, "twitter_share", "width=600, height=400");
}


function bindCitySearch() {
   var $city = $('.city-search');
   if ($city.length === 0) {
      return;
   }

   var setDefault = function () {
      var val = $.trim($city.val());
      if (!val) {
         $city.val($city.attr('data-default') || '');
      }
   };

   var options = {
      types: ['(cities)']
   };

   var onPlaceChange = function () {
      $city.blur();
      
      var place = autocomplete.getPlace();
      if (!place || !place.address_components) {
         setDefault();
         return false;
      }
      var url = $city.attr('data-url');
      if (!url) {
         setDefault();
         return false;
      }

      var city_data = {
         address_components: place.address_components,
         section: $city.attr('data-category') || 'home'
      };

      var onSuccess = function(data){
         if (data && data.link) {
            window.location.href = data.link.href;
         }
      };

      $('[data-columns]').addClass('wait');

      $.ajax({
         type: 'POST',
         url: url,
         data: JSON.stringify(city_data),
         success: onSuccess,
         error: function (jqXHR, textStatus, errorThrown) {
            $('[data-columns]').removeClass('wait');
            console.error(errorThrown);
         },
         dataType: 'json'
      });
   };

   var autocomplete = new google.maps.places.Autocomplete($city[0], options);
   google.maps.event.addListener(autocomplete, 'place_changed', onPlaceChange);

   $city.on('mousedown', function (e) {
      e.preventDefault();
      e.stopPropagation();
      $city[0].select();
      setDefault();
      return false;
   });

   $city.on('blur', function () {
      setDefault();
   });

   $city.on('keydown', function (e) {
      var val = $.trim($city.val());
      if (e.which == KEY_ENTER && val.search(/world/) !== -1) {
         e.preventDefault();
         e.stopPropagation();
         var cat = $city.attr('data-category');
         var url = cat ? '/routes/categories/' + cat : '/';
         window.location.href = url;
         return false;
      }
   });
   
   $(document).on('mousedown', function () {
      setDefault();
   });
}


function bindLoadMore() {
   $('#load-more').on('click', function () {
      var $btn = $(this).addClass('wait').prop('disabled', true);
      var href = $btn.attr('data-target-href');
      var page = $btn.attr('data-page');
      // TODO: rework views to remove the vars below
      var page_type = $btn.attr('data-page-type');
      var category_type = $btn.attr('data-category');

      $.ajax({
         type: "POST",
         url: href,
         data: {
            page: page,
            page_type: page_type,
            category_type: category_type
         }
      }).done(function (data) {
         $btn.removeClass('wait');

         if (!data || data.hide_button) {
            $btn.addClass('nomore').text($btn.attr('data-nomore'));
            if (!data) {
               return;
            }
         } else {
            $btn.prop('disabled', false);
         }

         var raw_html = data.raw_html;
         if (raw_html) {
            var colset = $('[data-columns]').eq(0).data('colset');
            raw_html = raw_html.replace(/\n+/gi, '').replace(/\s+/gi, ' ');
            $(raw_html).filter('.flow-item').each(function () {
               colset.append(this);
            });
         }
         $btn.attr('data-page', data.page);
      });
   });
}


function makeScrollTo(id) {
   return function () {
      var $el = $('#r-' + id);
      var off = $el.offset();
      if (off) {
         $('html, body').animate({
            scrollTop: off.top
         },

         function () {
            highlight($el.find('div').eq(0));
         }).focus();
      }
   };
}

function insertRealMap(sel, markers){
  var map = new GMaps({
    div: sel,
    zoom: 13,
    scrollwheel: false
  });

  var gmap = map.map
  var point;
  var markerBounds = new google.maps.LatLngBounds();
  var path = [];
  
  _.each(markers, function(m){
    map.addMarker({
      lat: m.lat,
      lng: m.lng, 
      title: m.title,
      click: makeScrollTo(m.id)
    });
    point = new google.maps.LatLng(m.lat, m.lng);
    markerBounds.extend(point);
    path.push([m.lat, m.lng]);
  });

  gmap.setCenter(markerBounds.getCenter());
  gmap.fitBounds(markerBounds);
  map.drawPolyline({
    path: path,
    strokeColor: '#1b60e8',
    strokeOpacity: 0.4,
    strokeWeight: 6
  });

  $('#expand-map').click(function(e){
      e.preventDefault();
      e.stopPropagation();
      var $this = $(this);
      var toheight = $this.hasClass('expanded') ? 300 : 500;
      $this.toggleClass('expanded');
      map.map.setOptions({disableDefaultUI: true});
      $('#map').animate(
          {'height': toheight + 'px'},
          300,
          function(){
            google.maps.event.trigger(map.map, "resize");
            map.map.setOptions({disableDefaultUI: false});
          }
      );
      return false;
  });

  return map;
}


function insertStaticMap(sel, markers){
  $('#expand-map').hide();
  if (markers.length === 0){
    return;
  }
  var $map = $(sel);
  var url = GMaps.staticMapURL({
    size: [$map.width(), $map.height()],
    lat: markers[0].lat,
    lng: markers[0].lng,
    markers: markers
  });
  $('<img/>').attr('src', url).appendTo($map);
  return $map[0];
}


function easeInOut(minValue, maxValue, totalSteps, actualStep, powr) {
   var delta = maxValue - minValue;
   var stepp = minValue + (Math.pow(((1 / totalSteps) * actualStep), powr) * delta);
   return Math.ceil(stepp);
}

function doBGFade($elem, startRGB, endRGB, finalColor, steps, intervals, powr) {
   if ($elem.bgFadeInt) {
      window.clearInterval($elem.bgFadeInt);
   }
   var actStep = 0;
   $elem.bgFadeInt = window.setInterval(

   function () {
      $elem.css("backgroundColor", "rgb(" + easeInOut(startRGB[0], endRGB[0], steps, actStep, powr) + "," + easeInOut(startRGB[1], endRGB[1], steps, actStep, powr) + "," + easeInOut(startRGB[2], endRGB[2], steps, actStep, powr) + ")");
      actStep++;
      if (actStep > steps) {
         $elem.css("backgroundColor", finalColor);
         window.clearInterval($elem.bgFadeInt);
      }
   }, intervals);
}

function highlight($elem) {
   var yellow = [241, 221, 104];
   var white = [255, 255, 255];
   var steps = 40;
   var intervals = 20;
   var powr = 4;
   doBGFade($elem, yellow, white, white, steps, intervals, powr);
}


function bindRemix() {
   var $remixModal = $('#circuit-remix');
   if (!$remixModal.length){
      return;
   }

   $remixModal.modal({
      show: false
   });

   $('section').on('click', '[data-remix]', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var $this = $(this);
      $remixModal.find('input[name=name]').val($this.attr('data-name'));
      $remixModal.find('select[name=category]').val($this.attr('data-cat'));
      $remixModal.find("#remix-route-name").html($this.attr('data-name'));
      $remixModal.find('input[name=adult_content]').attr(
	  'checked', ($this.attr('data-adult') == 'True') ? true : false
      );
      $remixModal.attr('action', $this.attr('data-remix'));
      $remixModal.modal('show');
   });
}


function bindActions() {
   bindToggleButtons();
   bindRadioButtons();
}


function bindToggleButtons() {
   $('section').on('click', '[data-toggle-class]', function (e) {
      e.preventDefault();
      e.stopPropagation();

      var $btn = $(this);
      var toggleClass = $btn.attr('data-toggle-class');
      var isOn = $btn.hasClass(toggleClass);

      // Optional confirm message
      var msg = $btn.attr('data-msg');
      if (msg && !confirm(msg)) {
         return false;
      }

      var newState = isOn ? 'off' : 'on';
      var newTitle = $btn.attr('data-title-' + newState);
      var newText = $btn.attr('data-text-' + newState);
      var url = $btn.attr('data-url-' + newState);

      // Update class
      $btn.toggleClass(toggleClass);

      // Update title
      if (newTitle) {
         if ($btn.attr('data-original-title')) {
            $btn.attr('data-original-title', newTitle);
         } else {
            $btn.attr('title', newTitle);
         }
      }

      // Update text
      if (newText) {
         $btn.find('span').text(newText);
      }

      // Post new state
      if (!url) {
         return false;
      }

      $.ajax({
         type: 'POST',
         url: url,
         success: function (data) {
            if (data && data.link) {
               window.location.href = data.link.href;
            }
         },
         error: function (jqXHR, textStatus, errorThrown) {
            console.error(errorThrown);
         },
         dataType: 'json'
      });
      return false;
   });
}


function bindRadioButtons() {
   $('section').on('click', '[data-val]', function (e) {
      e.preventDefault();
      e.stopPropagation();

      var $btn = $(this);
      var $group = $btn.parents('[data-radio]');
      var url = $group.attr('data-radio');
      var name = $group.attr('data-name');
      var value = $btn.attr('data-val');
      var newClass = $btn.attr('data-val-class');

      if ($group.attr('data-val') == value){
         // Resetting value
         value = 0;
         newClass = '';
      }
      $group.attr('data-val', value)
      $group[0].className = newClass;

      // Post new state
      if (!url) {
         return false;
      }
      var data = {};
      data[name] = value;

      $.ajax({
         type: 'POST',
         url: url,
         data: data,
         success: function (data) {
            if (data && data.link) {
               window.location.href = data.link.href;
            }
         },
         error: function (jqXHR, textStatus, errorThrown) {
            console.error(errorThrown);
         },
         dataType: 'json'
      });
      return false;
   });
}


function calcDistances() {
   var $coords = $('[data-coords]');
   if ($coords.length === 0 || typeof (GMaps) === 'undefined') {
      return;
   }

   var onError = function () {
      $coords.hide();
   };

   var onSuccess = function (position) {
      var here = [
         position.coords.latitude,
         position.coords.longitude
         ];

      $coords.each(function () {
         var $this = $(this);
         var latlng = $this.attr('data-coords').split(/\s*,\s*/);
         var lat = parseFloat(latlng[0], 10);
         var lng = parseFloat(latlng[1], 10);
         if (isNaN(lat) || isNaN(lng)) {
            return;
         }
         var distance = getDistance(here, [lat, lng]);
         $this.find('span').text(distance);
      });
   };

    GMaps.geolocate({
       success: onSuccess,
       error: onError,
       not_supported: onError,
       options: {maximumAge:300000} // 5min
    });
}


function toggle_more_cats_sidebar() {
   /* Simple css magic and collapse accordion plugin from bootstrap.
    * With ♥ PuercoP☯ P */
   var $iter = $('#more-cats-controller a');
   $iter.click(function () {
      $iter.toggleClass("show");
      $('#more-cats').collapse("toggle");
   });
}


function humanDate(time_str) {
   /* pass a str rep of date to get the human readable representation of the
    * difference. With ♥ PuercoP☯ P */
   var now = new Date();
   var yesterday = new Date(time_str);

   var diff_years = now.getYear() - yesterday.getYear();
   if (diff_years > 0) {
      if (diff_years === 1) {
         return diff_years + " year ago.";
      }
      return diff_years + " years ago.";
   }

   var diff_months = now.getMonth() - yesterday.getMonth();
   if (diff_months > 0) {
      if (diff_months === 1) {
         return diff_months + " month ago.";
      }
      return diff_months + " months ago.";
   }

   var diff_days = now.getDay() - yesterday.getDay();
   if (diff_days > 0) {
      if (diff_days === 1) {
         return diff_days + "day ago.";
      }
      return diff_days + " days ago.";
   }

   var diff_minutes = now.getMinutes() - yesterday.getMinutes();
   if (diff_minutes > 0) {
      if (diff_minutes === 1) {
         return diff_minutes + " minute ago.";
      }
      return diff_minutes + " minutes ago.";
   }

   return "Just now";
}


var PI_180 = Math.PI / 180;

function getDistance(latLng1, latLng2) {
   /*Calculate the distance between two set of coordinates.
    This is just an approximation and it'll be more off while nearer to
    the poles. */
   var lat1 = latLng1[0];
   var lon1 = latLng1[1];
   var lat2 = latLng2[0];
   var lon2 = latLng2[1];

   var R = 6371; // Radius of the earth in km
   var dLat = (lat2 - lat1) * PI_180; // Javascript functions in radians
   var dLon = (lon2 - lon1) * PI_180;
   var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * PI_180) * Math.cos(lat2 * PI_180) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
   var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
   var d = R * c; // Distance in km

   if (d < 1) {
      return Math.round(d * 1000) + ' m';
   }
   return Math.round(d * 10) / 10 + ' Km';
}

function setLastEmailIndex() {
    var lastIndex = $('.user-email').last().attr('data-index');
    $('ul.emails').attr('data-index', lastIndex);
}

function bindAccountSettings() {
    //Set current index to 0
 
    setLastEmailIndex();

    $('#append-email').on('click', function () {
        var $btn = $(this);
        var href = $btn.attr('data-target-href');
        var email = $('#email-candidate').val();
        
        $.ajax({
            type: "POST",
            url: href,
            data: {
                email: email
                }
            }).done(function (data) {
                //Do Stuff Here
                // Success
                if (data.status == 'OK') {
                    var nextIndex = (parseInt($('.user-email').last().attr('data-index')) + 1).toString();
                    
                    $('ul.emails').append('<li data-index="' + nextIndex + '"><span class="user-email not-verified"</span><span class="delete-email" data-index="' + nextIndex + '">X</span></li>');
                    $('#notifications').html('<p class="alert alert-success">Se te ha enviado un correo para verificar la dirección</p>');
                }

                // Error
                if(data.status == 'error') {
                    $('#notifications').html('<p class="alert alert-error">' + data.message + '</p>');
                }
                                 
                setLastEmailIndex();

                });
    });
   
    $('.delete-email').on('click', function () {

        var $btn = $(this);
        var href = $btn.attr('data-target-href');
        var index = $btn.attr('data-index');
        var email = $('.user-email[data-index="' + index + '"]').text();


        $.ajax({
            type: "POST",
            url: href,
            data: {
                email: email
            }
        }).done(function (data) {
            //Do Stuff Here
            if (data.status == 'OK') {
                
                $('.user-email').last().parent().remove()
                $('#notifications').html('<p class="alert alert-success">Se ha desasociado la cuenta de correo.</p>');
            };

            if (data.status == 'error') {
                $('#notifications').html('<p class="alert alert-error">' + data.message + '</p>');
            };
            setLastEmailIndex();
        });
    });
}



/* Auto send crsft middleware token in ajax events
 * taken from: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/ */
$(document).ajaxSend(function (event, xhr, settings) {
   function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
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

   function sameOrigin(url) {
      // url could be relative or scheme relative or absolute
      var host = document.location.host; // host + port
      var protocol = document.location.protocol;
      var sr_origin = '//' + host;
      var origin = protocol + sr_origin;
      // Allow absolute or scheme relative URLs to same origin
      // or any other URL that isn't scheme relative or absolute i.e relative.
      return (url == origin || url.slice(0, origin.length + 1) == origin + '/') || (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') || !(/^(\/\/|http:|https:).*/.test(url));
   }

   function safeMethod(method) {
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
   }

   if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
   }
});


/**
 * ShakeIt
 * Makes an element shake
 *
 * Usage: $('#my-input').shakeIt();
 *
 * @class shake
 * @param {Object} options
 */
jQuery.fn.shakeIt = function (options) {
   options = jQuery.extend({
      speed: 40,
      duration: 400,
      spread: 20
   }, options);

   return this.each(function () {
      var $this = jQuery(this);
      var k = (options.spread - 1) / 2

      var updatePos = function () {
            var leftPos = Math.floor(Math.random() * options.spread) - k;
            $this.css('left', leftPos + 'px');
         };

      var shakeIt = function () {
            $this.css('position', 'relative');
            var interval = setInterval(updatePos, options.speed);

            var stopIt = function () {
                  clearInterval(interval);
                  $this.css({
                     position: 'static'
                  });
               };
            setTimeout(stopIt, options.duration);
         };

      shakeIt();
   });
};
