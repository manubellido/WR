#! -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from common.utils.strings import multiple_whitespace_to_single_space

from user_profile.models import UserProfile
from user_profile.registration import strings
from user_profile.registration.validators import validate_free_email
from user_profile.registration.validators import validate_user_email

attrs_dict = {'class': 'required'}


class RegisterForm(forms.Form):

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'required',
            'placeholder': strings.FIRST_NAME_PLACEHOLDER,
            }),
        label='First Name',
        max_length=65,
        required=True,
    )

    last_name = forms.CharField(
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
        label=_("E-mail"),
        required=True
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password")
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password (again)")
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        email = multiple_whitespace_to_single_space(email).strip()
        return email

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(strings.PASSWORD_MATCH_ERROR)

        return cleaned_data


class OrgRegisterForm(forms.Form):

    corporate_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'required'}
        ),
        # Missing translations here
        label='Corporate Name',
        max_length=256,
        required=True,
    )

    short_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'required'}
        ),
        # Missing translations here
        label='Short Name',
        max_length=30,
        required=True
    )

    website = forms.URLField(
        # Missing translations here
        label='Website',
        required=False,
    )

    company_phone = forms.CharField(
        # Missing translations here
        label='Phone Number',
        max_length=20,
        required=False,
    )

    company_email = forms.EmailField(
        validators=[validate_free_email],
        widget=forms.TextInput(attrs={
            'class': 'required',
            'maxlength': 75,
            'type': 'email'
            }),
        # Missing translations here
        label='Company E-mail',
        required=True
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password")
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password (again)")
    )

    # Contact Person info

    contact_person = forms.CharField(
        # Missing translations here
        label='Contact Person\'s Name',
        max_length=128,
        required=True,
    )

    contact_person_phone = forms.CharField(
        # Missing translations here
        label='Contact Person\' Phone',
        max_length=20,
        required=False,
    )

    contact_person_email = forms.EmailField(
        validators=[validate_free_email],
        widget=forms.TextInput(attrs={
            'class': 'required',
            'maxlength': 75,
            'type': 'email'
            }),
        # Missing translations here
        label='Contact E-mail',
        required=True
    )

    contact_person_position = forms.CharField(
        # Missing translations here
        label='Position within the company',
        max_length=128,
        required=False
    )

    def clean_company_email(self):
        email = self.cleaned_data['company_email']
        email = multiple_whitespace_to_single_space(email).strip()
        return email

    def clean_contact_person_email(self):
        email = self.cleaned_data['contact_person_email']
        email = multiple_whitespace_to_single_space(email).strip()
        return email

    def clean(self):
        cleaned_data = super(OrgRegisterForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError(strings.PASSWORD_MATCH_ERROR)

        return cleaned_data


class RegisterInvitationForm(RegisterForm):

    email = forms.EmailField(
        validators=[validate_user_email],
        widget=forms.TextInput(attrs={
            'class': 'required',
            'maxlength': 75,
            'type': 'email'
            }),
        label=_("E-mail"),
        required=True
    )
