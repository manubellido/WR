# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
urlpatterns = patterns('',
    url(r'^', include('circuits.api.urls')),
    url(r'^', include('places.api.urls')),
    url(r'^', include('user_profile.api.urls')),
    url(r'^', include('notifications.api.urls')),
    url(r'^', include('googlemaps_localities.api.urls')),
)
if settings.ENABLE_HAYSTACK:
    urlpatterns += patterns('',
            url(r'^', include('website.api.urls')),
        )
