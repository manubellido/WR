# -*- coding: utf-8 -*-

"""
Settings for the rest app
"""

from django.conf import settings
from rest import constants


REST_FORCE_LANGUAGE = getattr(
    settings,
    'REST_FORCE_LANGUAGE',
    constants.REST_FORCE_LANGUAGE
)

REST_DEFAULT_LANGUAGE = getattr(
    settings,
    'REST_DEFAULT_LANGUAGE',
    constants.REST_DEFAULT_LANGUAGE
)
