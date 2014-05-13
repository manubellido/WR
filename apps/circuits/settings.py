# -*- coding: utf-8 -*-

from django.conf import settings
from circuits import constants

DEFAULT_CIRCUITS_OFFSET = getattr(
    settings,
    'DEFAULT_CIRCUITS_OFFSET',
    constants.DEFAULT_CIRCUITS_OFFSET
)

DEFAULT_CIRCUITS_LIMIT = getattr(
    settings,
    'DEFAULT_CIRCUITS_LIMIT',
    constants.DEFAULT_CIRCUITS_LIMIT
)

API_DEFAULT_CIRCUITS_OFFSET = getattr(
    settings,
    'API_DEFAULT_CIRCUITS_OFFSET',
    constants.DEFAULT_CIRCUITS_OFFSET
)

API_DEFAULT_CIRCUITS_LIMIT = getattr(
    settings,
    'API_DEFAULT_CIRCUITS_LIMIT',
    constants.DEFAULT_CIRCUITS_LIMIT
)

CIRCUIT_COLUMN_SIZES = getattr(
    settings,
    'CIRCUIT_COLUMN_SIZES',
    constants.CIRCUIT_COLUMN_SIZES
)

CIRCUIT_STOP_COLUMN_SIZES = getattr(
    settings,
    'CIRCUIT_STOP_COLUMN_SIZES',
    constants.CIRCUIT_STOP_COLUMN_SIZES
)
