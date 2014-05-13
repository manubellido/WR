# -*- coding: utf-8 -*-

"""
Static string for website app
"""

from django.utils.translation import ugettext_lazy as _


GENERIC_SECTION_NAME = _(u'Recommended routes')

LOCAL_CIRCUITS_TITLE = _(u'%(section_name)s in %(location_name)s')

# Errors

CHANGE_LOCATION_ERROR = _(
    u'A JSON document with the address components and the current '
    u'section of the page must be sent via the POST method.'
)

CHANGE_LOCATION_DOCUMENT_ERROR = _(
    u'The document sent in the body of the request is not valid JSON or '
    u'does not match the requirements.'
)

MISSING_PAGE_PARAM_ERROR = _(u'Missing POST parameter: page')

SECTION_IS_INVALID = _(u'The section sent was not recognized')

GMAC_NOT_FOUND = _(u'No component address object could be retrieved')
