# -*- coding:utf-8 -*-
"""
Imports defaults into Django's settings
"""
from imageresizer.conf import defaults
from django.conf import settings

SORL_THUMBNAIL_PREFIX = 'THUMBNAIL_'
IMAGERESIZER_PREFIX = 'IMAGERESIZER_'

# set defaults into settings
for setting in dir(defaults):
    if setting == setting.upper() and not hasattr(settings, setting):
        setattr(settings, setting, getattr(defaults, setting))

# write imageresizer's settings into thumbnail's
for setting in dir(settings):
    if setting.startswith(SORL_THUMBNAIL_PREFIX):
        setattr(settings, setting, getattr(
                settings,
                IMAGERESIZER_PREFIX + setting[len(SORL_THUMBNAIL_PREFIX):]))
