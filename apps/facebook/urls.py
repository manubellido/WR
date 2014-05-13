# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from facebook import views

urlpatterns = patterns('',

    url(r'^login/?$',
        views.facebook_login,
        name='facebook_login'),

    url(r'^login/redirection-end/?$',
        views.facebook_login_redirection_end,
        name='facebook_login_redirection_end'),

    url(r'^authorization/$',
        views.facebook_authorization,
        name='facebook_authorization'),

    url(r'^authorization/redirection-end/?$',
        views.facebook_authorization_redirection_end,
        name='facebook_authorization_redirection_end'),
)
