# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from user_profile.api import resources

urlpatterns = patterns('',
    url(
        r'^users/(?P<user_id>[\d]+)/is_follower/?$',
        resources.IsFollowerFunction.as_view(),
        name='is_follower_function_resource'
    ),
    url(
        r'^users/(?P<user_id>[\d]+)/is_following/?$',
        resources.IsFollowingFunction.as_view(),
        name='is_following_function_resource'
    ),
    url(
        r'^users/(?P<user_id>[\d]+)/follow/?$',
        resources.FollowController.as_view(),
        name='user_follow_controller_resource'
    ),
    url(
        r'^users/(?P<user_id>[\d]+)/unfollow/?$',
        resources.UnfollowController.as_view(),
        name='user_unfollow_controller_resource'
    ),
    url(
        r'^users/(?P<user_id>[\d]+)/?$',
        resources.UserResource.as_view(),
        name='user_resource'
    ),
    url(
        r'^users/me/?$',
        resources.UserMeFunction.as_view(),
        name='user_me_function_resource'
    ),
    # registration
    url(
        r'^registration/lookup_email/?$',
        resources.RegistrationEmailLookupFunction.as_view(),
        name='lookup_email_function_resource'
    ),
    url(
        r'^registration/register/?$',
        resources.RegistrationController.as_view(),
        name='registration_controller_resource'
    ),
    
)
