# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError


# VALIDATE TO EMTPY STRING
def validate_not_zero(value):
    if int(value) == 0:
        raise ValidationError(u'Not valid category')
