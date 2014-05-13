# -*- coding: utf-8 -*-

from common.datastructures import Enumeration


PSV_DICT_NAME = 'persistent_session_vars'

# IMPORTANT
# languages has to be a mirror of settings.LANGUAGES
LANGUAGE_CHOICES = Enumeration([
    (1, 'ENGLISH', 'en'),
    (2, 'SPANISH', 'es')
])

REGISTRATION_CODE_RANGE_START = 1000
REGISTRATION_CODE_RANGE_END = 999999

EMBEDDING_FAIL_VALUES = [False]

EMBEDDING_STYLE_CHOICES = (
    (1, 'Cards'),
    (2, 'List')
    )
