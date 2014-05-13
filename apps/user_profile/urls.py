# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse

from user_profile import views
from user_profile.auth import views as auth_views


urlpatterns = patterns(
    '',
    url(r'^(?P<user_id>\d+)/$',
        views.profile_landing_page,
        name='show_user_profile',
        ),
    url(r'^(?P<user_id>\d+)/profile/$',
        views.show_profile,
        name='show_user_profile_info',
        ),
    url(r'^(?P<user_id>\d+)/followers/$',
        views.show_followers,
        name='show_user_profile_followers',
        ),
    url(r'^(?P<user_id>\d+)/following/$',
        views.show_following,
        name='show_user_profile_following',
        ),
    url(r'^routes/views.favorites/$',
        views.favorite_routes_view,
        name='favorite_routes',
        ),
    url(r'^(?P<user_id>\d+)/favorites/$',
        views.user_favorite_routes,
        name='user_favorite_routes',
        ),
    url(r'^(?P<user_id>\d+)/circuits/$',
        views.user_circuit_list,
        name='user_circuit_list',
        ),
    url(r'^(?P<user_id>\d+)/circuits/embedform/$',
        views.user_circuit_list_embed_form,
        name='user_circuit_list_embed_form',
        ),
    url(r'^(?P<user_id>\d+)/follow/$',
        views.follow_user,
        name='follow_user',
        ),
     url(r'^verify_email/(?P<verification_code>\d+)/$',
        auth_views.verify_email,
        name='verify_user_email',
        ),
    )
