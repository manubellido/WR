# -*- coding: utf-8 -*-

from django import conf

from user_profile import constants

VERIFICATION_MAIL_SUBJECT = u'Worldrat: Verifica tu email'
PSV_DICT_NAME = getattr(conf, 'PSV_DICT_NAME', constants.PSV_DICT_NAME)
