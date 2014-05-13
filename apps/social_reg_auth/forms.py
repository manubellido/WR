# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from social_reg_auth import strings
from user_profile.registration.validators import validate_free_email

class TwitterUserForm(forms.Form):
    first = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'required',
            'placeholder': strings.FIRST_NAME_PLACEHOLDER,
            }),
        label='First Name',
        max_length=65,
        required=True,
    )

    last = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'required',
            'placeholder': strings.LAST_NAME_PLACEHOLDER,
            }),
        label='First Name',
        max_length=65,
        required=True
    )

    email = forms.EmailField(
        validators=[validate_free_email],
        widget=forms.TextInput(attrs={
            'class': 'required',
            'maxlength': 75,
            'type': 'email'
            }),
        label=_("Email"),
        required=True
    )
