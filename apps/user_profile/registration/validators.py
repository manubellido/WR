# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from user_profile import strings
from closed_beta.models import Invitation

def validate_free_email(email):
    """
    Check if email is a valid email and if said email isn't used by another
    user. Raise a validation error. Meant to be used by the form's clean
    method
    """
    try:
        user = User.objects.get(email=email)
        raise ValidationError(strings.EMAIL_ALREADY_USED % {'email': email})
    except User.DoesNotExist:
        try:
            invite = Invitation.objects.get(email=email)
            raise ValidationError(strings.EMAIL_ALREADY_USED % {'email': email})
        except Invitation.DoesNotExist:
            pass

def validate_user_email(email):
    """
    Check if email is used by another user
    """
    try:
        user = User.objects.get(email=email)
        raise ValidationError(strings.EMAIL_ALREADY_USED % {'email': email})
    except User.DoesNotExist:
        pass
