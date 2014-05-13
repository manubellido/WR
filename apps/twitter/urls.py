# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from twitter import views

urlpatterns = patterns('',

    url(r'^authorization/$',
        views.twitter_authorization,
        name='twitter_authorization'),

    url(r'^authorization/redirection-end/?$',
        views.twitter_authorization_redirection_end,
        name='twitter_authorization_redirection_end'),
)
