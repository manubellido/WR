# -*- coding: utf-8 -*-

from googlemaps_localities import strings

ADDRESS_COMPONENT_TYPE_CHOICES = (
    ('locality', strings.GMACTYPE_LOCALITY),
    ('administrative_area_level_3', strings.GMACTYPE_AREA_LEVEL_3),
    ('administrative_area_level_2', strings.GMACTYPE_AREA_LEVEL_2),
    ('administrative_area_level_1', strings.GMACTYPE_AREA_LEVEL_1),
    ('country', strings.GMACTYPE_COUNTRY),
)

REVERSE_GEOLOCATION_ERROR_LOG = '/tmp/worldrat-reverse-geolocation-errors.log'

LATITUDE_MAX_VALUE = 90.0
LATITUDE_MIN_VALUE = -90.0

LONGITUDE_MAX_VALUE = 180.0
LONGITUDE_MIN_VALUE = -180.0
