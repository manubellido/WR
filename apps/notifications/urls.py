# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse

urlpatterns = patterns('notifications.views',
        url(r'^$',
            'show_activity',
            name='show_activity',
        ),
    )
