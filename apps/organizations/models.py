# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sites.models import Site
from registration.models import RegistrationProfile

from common.models import AuditableModel
from organizations import strings


class Organization(AuditableModel):

    user = models.OneToOneField(User,
        verbose_name=strings.ORGANIZATION_USER,
        related_name='organization'
    )

    corporate_name = models.CharField(
        verbose_name=strings.ORGANIZATION_CORPORATE_NAME,
        max_length=256,
    )

    short_name = models.CharField(
        verbose_name=strings.ORGANIZATION_SHORT_NAME,
        max_length=64,
    )

    website = models.CharField(
        verbose_name=strings.ORGANIZATION_WEBSITE,
        max_length=256,
        blank=True,
        null=True
    )

    company_phone = models.CharField(
        verbose_name=strings.ORGANIZATION_COMPANY_PHONE,
        max_length=20,
        blank=True,
        null=True
    )

    company_email = models.CharField(
        verbose_name=strings.ORGANIZATION_COMPANY_EMAIL,
        max_length=75,
    )

    contact_person = models.CharField(
        verbose_name=strings.ORGANIZATION_CONTACT_PERSON,
        max_length=128,
    )

    contact_person_phone = models.CharField(
        verbose_name=strings.ORGANIZATION_CONTACT_PERSON_PHONE,
        max_length=20,
        blank=True,
        null=True
    )

    contact_person_email = models.CharField(
        verbose_name=strings.ORGANIZATION_CONTACT_PERSON_EMAIL,
        max_length=75,
    )

    contact_person_position = models.CharField(
        verbose_name=strings.ORGANIZATION_CONTACT_PERSON_POSITION,
        max_length=128,
        blank=True,
        null=True
    )

    approved = models.BooleanField(
        verbose_name=strings.ORGANIZATION_APPROVED,
        default=False
    )

    mail_sent = models.BooleanField(
        verbose_name=strings.ORGANIZATION_ACTIVATION_MAIL_SENT,
        default=False
    )

    def __unicode__(self):
        return self.short_name

    def approve(self,
                template='mails/launching.html',
                #template='closed_beta/invitation_approved_mail.html',
                sender=None):
        reg_profile = RegistrationProfile.objects.get(user=self.user)

        if not self.mail_sent:
            current_site = Site.objects.get_current()
            reg_profile.send_activation_email(current_site)

            self.approved = True
            self.mail_sent = True
            self.save()

    def save(self, *args, **kwargs):
        result = super(Organization, self).save(*args, **kwargs)
        if self.approved and not self.mail_sent:
            self.approve()
        return result
