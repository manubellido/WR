# -*- coding: utf-8 -*-

import json

from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from closed_beta.models import Invitation
from closed_beta.forms import InvitationForm, AdditionalInvitationsForm
from user_profile.registration.validators import validate_free_email
from user_profile import strings
from closed_beta import strings as cbstrings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage

def invitation_form(request, template=None):
    form = InvitationForm()

    if request.method == 'POST':
        form = InvitationForm(request.POST)
        try:
            validate_email(request.POST.get('email',''))
        except ValidationError:
            return render(request,
                    'closed_beta/invitation_invalid_email.html',
                    {},
            )

        if form.is_valid():
            form.save()
            ### Send mail

            return render(request,
                    'closed_beta/invitation_sent.html',
                    {},
            )
        else:
            return render(request,
                    'closed_beta/invitation_email_already_sent.html',
                    {},
            )

    return render(request,
            'closed_beta/invitation_form.html',
            {
                'form': form,
            },
        )

def is_email_valid(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        response = {}
        response['email'] = email
        if email:
            try:
                validate_email(email)
                try:
                    validate_free_email(email)
                    response['is_valid'] = True
                    response['msg'] = unicode(strings.VALID_EMAIL)
                except ValidationError:
                    response['is_valid'] = False
                    response['error'] = unicode(strings.EMAIL_ALREADY_USED)
            except ValidationError:
                    response['is_valid'] = False
                    response['error'] = unicode(
                        strings.INVALID_EMAIL % {'email': email}
                        )
        else:
            response['is_valid'] = False
            response['error'] = unicode(strings.NO_EMAIL)

        return HttpResponse(json.dumps(response),
                            mimetype='application/json')

def send_invitations_form(request):
    form = AdditionalInvitationsForm()
    invitations_left = request.user.userprofile.invitations_left

    if request.method == 'POST':
        form = AdditionalInvitationsForm(request.POST)
        response = {}
        if form.is_valid():
            email_list = form.cleaned_data['emails']
            i=0
            for email in email_list:
                i = i + 1
                invitation = Invitation.create_invitation(
                    email=email,
                )
                invitation.approve(
                    template='closed_beta/youve_been_invited.html',
                    sender=request.user
                )
            #Remove n invitation from user
            current = request.user.userprofile.invitations_left
            request.user.userprofile.invitations_left = current - i
            request.user.userprofile.save()

            response['is_valid'] = True
            response['msg'] = unicode(cbstrings.INVITATIONS_SENT)
        else:
            response['is_valid'] = False
            response['error'] = unicode(cbstrings.CANNOT_SENT_INVITATIONS)

        return HttpResponse(json.dumps(response),
                            mimetype='application/json')


    total = 0
    if invitations_left >= 5:
        total = 5
    else:
        total = invitations_left

    return render(request,
            'closed_beta/additional_invitations_form.html',
            {
                'form': form,
                'own_profile': True,
                'wr_user': request.user,
                'range': range(total),
            },
        )
