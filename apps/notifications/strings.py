# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

NOTIFIABLE_EVENT_VERBOSE_NAME = _(u'Notifiable event')
NOTIFIABLE_EVENT_VERBOSE_NAME_PLURAL = _('Notifiable events')
NOTIFIABLE_EVENT_OWNER = _(u'Owner')
NOTIFIABLE_EVENT_NOTIFICATION_TYPE = _(u'Notification type')
NOTIFIABLE_EVENT_INFO = _(u'Metadata')
NOTIFIABLE_EVENT_PROCESSED = _(u'Processed')
NOTIFIABLE_EVENT_PROCESSED_AT = _(u'Date and time of processing')

NOTIFICATION_VERBOSE_NAME = _(u'Notification')
NOTIFICATION_VERBOSE_NAME_PLURAL = _(u'Notifications')
NOTIFIED_USER = _(u'Notified user')
NOTIFICATION_INFO = _(u'Notification info')
NOTIFICATION_TYPE = _(u'Notification type')
NOTIFICATION_DISPLAYED = _(u'Notification displayed')

CIRCUIT_CREATED = _(u'Route created')
CIRCUIT_FAVORITED = _(u'Route added to favorites')
CIRCUIT_REMIXED = _(u'Route remixed')
CIRCUIT_UPDATED = _(u'Route updated')
USER_FOLLOWED = _(u'Followed user')
CONTENT_SHARED = _(u'Shared content')

# Email notifications strings
EMAIL_NOTIFICATION_SUBJECT = _(u'Worldrat Notification')

# needs follow feature
CIRCUIT_CREATED_EMAIL_NOTIFICATION = _(u'A new route was created by \
    one of the users that you follow.')
CIRCUIT_FAVORITED_EMAIL_NOTIFICATION = _(u'Your route "%(route)s" has been \
    favorited by %(user)s.')
CIRCUIT_REMIXED_EMAIL_NOTIFICATION = _(u'Your route "%(route)s" has been\
     remixed by %(user)s')
# needs follow feature
CIRCUIT_UPDATED_EMAIL_NOTIFICATION = _(u'One of the users you follow \
    updated his route.')
# needs follow feature
USER_FOLLOWED_EMAIL_NOTIFICATION = _(u'You are now beeing followed.')
# needs follow feature
CONTENT_SHARED_EMAIL_NOTIFICATION = _(u'User x has shared content.')

# API
NOTIFICATION_COLLECTION_NAME = _(u'Notifications')
NON_EXISTANT_NOTIFICATION = _(u'Non existant notification')
