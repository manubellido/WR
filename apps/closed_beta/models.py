# -*- coding: utf-8 -*-

import random

from django.contrib.gis.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage

from common.models import AuditableModel
from closed_beta import strings, constants


class Invitation(AuditableModel):

    email = models.EmailField(
        verbose_name=strings.INVITATION_EMAIL,
        unique=True,
    )

    ipaddr = models.GenericIPAddressField(
        verbose_name=strings.INVITATION_IPADDR,
        protocol='both',
        unpack_ipv4=True,
        blank=True,
        null=True,
    )

    approved = models.BooleanField(
        verbose_name=strings.INVITATION_APPROVED,
        default=False
    )

    mail_sent = models.BooleanField(
        verbose_name=strings.INVITATION_MAIL_SENT,
        default=False
    )

    used = models.BooleanField(
        verbose_name=strings.INVITATION_USED,
        default=False
    )

    code = models.BigIntegerField(
        verbose_name=strings.INVITATION_CODE,
        blank=True,
        null=True
    )

    def __unicode__(self):
        return strings.INVITATION_UNICODE % {'invite': self.code}

    @staticmethod
    def generate_invitation_code():
        result = None
        while result is None:
            code = random.randint(
                constants.INVITATION_CODE_RANGE_START,
                constants.INVITATION_CODE_RANGE_END
            )
            if Invitation.objects.filter(code=code).exists():
                continue
            else:
                result = code

        return result

    @staticmethod
    def create_invitation(email, ipaddr=None):
        code = Invitation.generate_invitation_code()
        obj = Invitation(
            email=email,
            ipaddr=ipaddr,
            approved=False,
            code=code
        )
        obj.save()
        return obj

    def approve(self,
                #template='mails/launching.html',
                template='closed_beta/invitation_approved_mail.html',
                sender=None):
        ##Mail for newer users
        if not self.mail_sent:
            current_site = Site.objects.get_current()

            destination_url = '%s://%s%s?%s=%s' % (
                settings.CLOSED_BETA_DESTINATION_LINK_PROTOCOL,
                current_site.domain,
                reverse(settings.CLOSED_BETA_DESTINATION_VIEW_NAME),
                settings.CLOSED_BETA_INVITATION_PARAM_NAME,
                self.code
            )

            ctx_dict = {
                'code': self.code,
                'destination_url': destination_url,
                'STATIC_PREFIX': settings.STATIC_PREFIX,
            }

            if sender and sender.get_full_name():
                ctx_dict['sender'] = sender.get_full_name()

            message = render_to_string(
                template,
                ctx_dict
            )
            msg = EmailMessage(
                    settings.INVITATION_MAIL_SUBJECT,
                    message, settings.EMAIL_DEFAULT_FROM_VALUE, [self.email])
            msg.content_subtype = "html"
            msg.send()

            self.approved = True
            self.mail_sent = True
            self.save()

    def save(self, *args, **kwargs):
        result = super(Invitation, self).save(*args, **kwargs)
        if self.approved and not self.mail_sent:
            self.approve()
        return result
