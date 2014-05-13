# -*-  coding: utf-8 -*-

from django.conf import settings
from common.utils.math.bases import BaseConverter
from common.utils.strings import str_in_chunks

base99 = BaseConverter(settings.DECIMAL_SCRAMBLER_DIGITS)

def scramble(number):
    number += settings.DECIMAL_SCRAMBLER_OFFSET
    return ''.join(base99.from_decimal(number))

def unscramble(number):
    number_in_digits = str_in_chunks(
        number, 
        settings.DECIMAL_SCRAMBLER_DIGIT_SIZE
    )
    return base99.to_decimal(number_in_digits)
