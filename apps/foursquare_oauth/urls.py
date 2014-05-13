# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from foursquare_oauth import views

urlpatterns = patterns('',

    url(r'^authorization/$',
        views.foursquare_authorization,
        name='foursquare_authorization'),

    url(r'^authorization/redirection-end/?$',
        views.foursquare_authorization_redirection_end,
        name='foursquare_authorization_redirection_end'),
)
