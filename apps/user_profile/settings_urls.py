# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse

urlpatterns = patterns('',
    url(r'^profile$',
        'user_profile.views.edit_profile',
        name='edit_profile'),
    #url(r'^$',
    #    'user_profile.views.account_settings',
    #    name='account_settings'),
)
