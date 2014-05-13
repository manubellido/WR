# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from social_reg_auth import views

urlpatterns = patterns('',
    url(r'^facebook/?$',
        views.facebook_registration,
        name='facebook_registration'
    ),

    url(r'^facebook_callback/?$',
        views.facebook_registration_callback,
        name='facebook_registration_callback'
    ),

    url(r'^facebook/unlink?$', 
        views.facebook_unlink, 
        name="facebook_unlink"
    ),

    # TWITTER

    # First leg of the authentication journey...
    url(r'^twitter/?$', 
        views.begin_auth, 
        name="twitter_login"
    ),

    url(r'^twitter/unlink?$', 
        views.twitter_unlink, 
        name="twitter_unlink"
    ),

    url(r'^twitter/register/?$', 
        views.new_twitter_user, 
        name="twitter_register"
    ),

    url(r'^twitter/thanks/?$', 
        views.thanks, 
        name="twitter_callback"
    ),
)
