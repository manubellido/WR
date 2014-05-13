# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

INVITATION_EMAIL = _(u'Email')
INVITATION_IPADDR = _(u'IP Address')
INVITATION_APPROVED = _(u'Approved?')
INVITATION_MAIL_SENT = _(u'Mail sent?')
INVITATION_USED = _(u'Used?')
INVITATION_CODE = _(u'Invite code')
INVITATION_UNICODE = _(u'Invite %(invite)s')
INVITATION_APPROVE_ACTION = _(u'Approve invites')

INVITATION_EMAILS_LIST = _(u'Invite email list')

# Errors

ALREADY_USED_FOR_INVITATION = _(
    u'Rat trouble! This email has already been invited '
    u'to the beta! Please try another :-\)'
)


CANNOT_SENT_INVITATIONS = _(
    u'We werent able to sent the invitations.'
)

INVITATIONS_SENT = _( u'Invitations Sent')
