# -*- coding: utf-8 -*-

from common.datastructures import Enumeration 
from suggestions import strings


SUGGESTION_SOURCE_CHOICES = Enumeration([
    (1, 'FACEBOOK', strings.SOURCE_FACEBOOK),
    (2, 'TWITTER', strings.SOURCE_TWITTER),
    ])
