# -*- coding: utf-8 -*- 

from common.datastructures import Enumeration
from notifications import strings

NOTIFICATION_TYPE_CHOICES = Enumeration([
    (1, 'CIRCUIT_CREATED', strings.CIRCUIT_CREATED),
    (2, 'CIRCUIT_FAVORITED', strings.CIRCUIT_FAVORITED),
    (3, 'CIRCUIT_REMIXED', strings.CIRCUIT_REMIXED),
    (4, 'CIRCUIT_UPDATED', strings.CIRCUIT_UPDATED),
    (5, 'USER_FOLLOWED', strings.USER_FOLLOWED),
    (6, 'CONTENT_SHARED', strings.CONTENT_SHARED)
])


# API
API_DEFAULT_NOTIFICATIONS_LIMIT = 10
API_DEFAULT_NOTIFICATIONS_OFFSET = 0
