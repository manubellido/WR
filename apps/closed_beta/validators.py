# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User

from user_profile.registration.validators import validate_free_email

def validate_email_list(text):
    print text
    email_list = text.split(',')

    for email in email_list:
        try:
            validate_email(email)
            validate_free_email(email)
        except ValidationError:
            raise ValidationError('Algunos de los correos que ingresaste están incorrectos o ya son parte de Worldrat, por favor revisa el formulario e intenta otra vez.')
