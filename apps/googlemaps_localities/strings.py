# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

GMACTYPE_LOCALITY = _(u'Locality')
GMACTYPE_AREA_LEVEL_1 = _(u'Administrative Area Level 1')
GMACTYPE_AREA_LEVEL_2 = _(u'Administrative Area Level 2')
GMACTYPE_AREA_LEVEL_3 = _(u'Administrativa Area Level 3')
GMACTYPE_COUNTRY = _(u'Country')

ADDRESS_COMPONENT = _(u'Google Maps Address Component')
ADDRESS_COMPONENT_PLURAL = _(u'Google Maps Address Components')

GMAC_SHORT_NAME = _(u'Short name')
GMAC_LONG_NAME = _(u'Long name')
GMAC_LOCATION = _(u'Location')
GMAC_FORMATTED_NAME = _(u'Formatted name')
GMAC_SLUG = _(u'Slug')
GMAC_COMPONENT_TYPE = _(u'Type')
GMAC_PARENT = _(u'Parent')
GMAC_LOCATION = _(u'Location')
GMAC_NORTHEAST_BOUND = _(u'Bounds (Northeast)')
GMAC_SOUTHWEST_BOUND = _(u'Bounds (Southwest)')
GMAC_NORTHEAST_VIEWPORT = _(u'Viewport (Northeast)')
GMAC_SOUTHWEST_VIEWPORT = _(u'Viewport (Southeast)')
GMAC_CREATED_AT = _(u'Created at')
GMAC_UPDATED_AT = _(u'Updated at')

# API

MISSING_COORDINATES_INFORMATION = _(
    u'Information of the latitude and/or longitude is missing '
    u'from the request'
)

WRONG_LATITUDE_VALUE = _(
    u'The value for the latitude must be a real number in the '
    u'range of -90.0 to +90.0'
)

WRONG_LONGITUDE_VALUE = _(
    u'The value for the longitude must be a real number in the '
    u'range of -180.0 to +180.0'
)

GMAC_LIST_MISSING = _(
    u'The request did not included a list of GMAC objects in '
    u'its body properly represented as a JSON document'
)

GMAC_NOT_FOUND = _(
    u'No GMAC object could be found associated to the data sent'
)

GMAC_JSON_NOT_PARSED = _(
    u'The contents of the body of the request could not be properly '
    u'parsed as JSON information'
)
