# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse

urlpatterns = patterns('closed_beta.views',
    url(r'^invitation/$',
        'invitation_form',
        name='request_invitation',
    ),
    url(r'^additional_invitations/$',
        'send_invitations_form',
        name='send_invitations',
    ),
    url(r'^is_email_valid/$',
        'is_email_valid',
        name='is_email_valid',
        )
)
