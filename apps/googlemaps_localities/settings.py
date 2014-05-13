# -*- coding: utf-8 -*-

from django.conf import settings
from googlemaps_localities import constants

REVERSE_GEOLOCATION_ERROR_LOG = getattr(settings,
    'REVERSE_GEOLOCATION_ERROR_LOG',
    constants.REVERSE_GEOLOCATION_ERROR_LOG
)
