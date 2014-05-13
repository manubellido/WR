# -*- coding: utf-8 -*-

from django import forms

from common.utils.strings import multiple_whitespace_to_single_space
from user_profile.registration.validators import validate_free_email
from closed_beta.models import Invitation
from closed_beta import strings
from closed_beta.validators import validate_email_list


class InvitationForm(forms.Form):
    """
    Form must check if the email is unique
    """

    email = forms.EmailField(
        validators=[validate_free_email],
        widget=forms.TextInput(attrs={'max_length': 75}),
        label=strings.INVITATION_EMAIL
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        email = multiple_whitespace_to_single_space(email).strip()
        # Check if the email has already an unused invitation
        if Invitation.objects.filter(email=email).exists():
            raise forms.ValidationError(strings.ALREADY_USED_FOR_INVITATION)
        else:
            return email

    def save(self, ipaddr=None):
        invitation = Invitation.create_invitation(
            email=self.cleaned_data['email'],
            ipaddr=ipaddr
        )
        return invitation

class AdditionalInvitationsForm(forms.Form):
    emails = forms.CharField(
        validators=[validate_email_list],
        widget=forms.Textarea(attrs={
                'rows': '',
                'cols': ''
            }),
        label=strings.INVITATION_EMAILS_LIST
    )

    def clean_emails(self):
        emails = self.cleaned_data['emails']
        email_list = emails.split('\n')
        return email_list
