# -*- coding: utf-8 -*-

from django.conf import settings
from places import constants

FS_API_VERSION = getattr(settings, 'MY_VAR', constants.FS_API_VERSION)

