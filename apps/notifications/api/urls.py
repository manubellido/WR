# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from notifications.api import resources

urlpatterns = patterns('',
    url(
        r'^users/(?P<user_id>[\d]+)/notifications$',
        resources.UserNotificationCollection.as_view(),
        name='notification_collection_resource'
    ),
        url(
        r'^notifications/(?P<notification_id>[\d]+)$',
        resources.NotificationResource.as_view(),
        name='notification_resource'
    ),
)
