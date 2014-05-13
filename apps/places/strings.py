# -*- coding: utf-8 -*-

"""
Static string for places app
"""

from django.utils.translation import ugettext_lazy as _

FS_COUNTRY_VERBOSE_NAME = _(u'Country')
FS_COUNTRY_VERBOSE_NAME_PLURAL = _(u'Countries')
FS_COUNTRY_NAME = _(u'Name')

FS_STATE_VERBOSE_NAME = _(u'State')
FS_STATE_VERBOSE_NAME_PLURAL = _(u'States')
FS_STATE_NAME = _(u'State')
FS_STATE_COUNTRY = _(u'Country')

FS_CITY_VERBOSE_NAME = _(u'City')
FS_CITY_VERBOSE_NAME_PLURAL = _(u'Cities')
FS_CITY_NAME = _(u'Name')
FS_CITY_STATE = _(u'State')

PLACE_VERBOSE_NAME = _(u'Place')
PLACE_VERBOSE_NAME_PLURAL = _(u'Places')
PLACE_NAME = _(u'Place name')
PLACE_ADDRESS = _(u'Address')
PLACE_COUNTRY = _(u'Country')
PLACE_LOCALITY = _(u'Locality')
PLACE_COORDINATES = _(u'Coordinates')
PLACE_PHONE_NUMBER = _(u'Telephone')
PLACE_WEBSITE = _(u'Website')
PLACE_CITY = _(u'Place city')
PLACE_COORDINATES = _(u'Coordinates')
PLACE_PHONE_NUMBER = _(u'Telephone')
PLACE_WEBSITE = _(u'Website')
PLACE_TWITTER_ACCOUNT = _(u'Twitter account')
PLACE_TYPE = _(u'Place type')
PLACE_CROSSSTREET = _(u'Place reference')

PLACETYPE_RELATION = _(u'Place type relationship')
PLACETYPE_NAME = _(u'Place type name')
PLACETYPE_PLURALNAME = _(u'Place type names')
PLACETYPE_SHORTNAME = _(u'Short place type name')
PLACETYPE_PREFIX = _(u'Place type prefix')
PLACETYPE_SIZES = _(u'Icon sizes')
PLACETYPE_ICONNAME = _(u'Icon format')
PLACETYPE_VERBOSE_NAME = _(u'Place type')
PLACETYPE_VERBOSE_NAME_PLURAL = _(u'Place types')

DONE_PLACE_VERBOSE_NAME = _(u'Done place register')
DONE_PLACE_VERBOSE_NAME_PLURAL = _(u'Done place registers')
DONE_PLACE_PLACE = _(u'Place')
DONE_PLACE_USER = _(u'User')
DONE_PLACE_IPADDR = _(u'IP address')
DONE_PLACE_COORDINATES = _(u'Coordinates')
DONE_PLACE_CREATED_INPLACE = _(u'¿From place?')

DONE_PLACE_UNICODE = _(u'User "%(user)s" has marked place "%(place)s" as done')

# API
NON_EXISTANT_PLACE = _(u'Place with identifier %(place_id)s does not exist')
PLACE_ALREADY_DONE = _(u'Place is already marked as Done')
PLACE_NOT_DONE = _(u'Place is not marked as Done')

UNKNOWN_PLACE_TYPE = _(u'No place type found under the token %(placetype_id)s')
PLACE_TYPE_COLLECTION = _(u'Place type collection')
