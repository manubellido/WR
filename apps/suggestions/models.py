# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.contrib.auth.models import User

from common.models import AuditableModel
from suggestions import constants, strings


class FBInviteSuggestion(AuditableModel):
    #Falta implementar que no se repitan
    suggesting_to = models.ForeignKey(User,
        verbose_name=strings.FB_RECEIVING_USER
        )

    suggested_fb_id = models.CharField(
        verbose_name=strings.SUGGESTED_FB_ID,
        max_length=50,
        )

    invite_sent = models.BooleanField(
        verbose_name=strings.FB_INVITE_SENT,
        default=False
        )

    invite_accepted = models.BooleanField(
        verbose_name=strings.FB_INVITE_ACCEPTED,
        default=False
        )

    class Meta:
        verbose_name = strings.FB_INVITE_VERBOSE_NAME
        verbose_name_plural = strings.FB_INVITE_VERBOSE_NAME_PLURAL
        unique_together = (('suggesting_to', 'suggested_fb_id'))


class TwitterInviteSuggestion(AuditableModel):
    suggesting_to = models.ForeignKey(User,
        verbose_name=strings.TWITTER_RECEIVING_USER
        )

    suggested_twitter_id = models.CharField(
        verbose_name=strings.SUGGESTED_TWITTER_ID,
        max_length=50,
        )

    invite_sent = models.BooleanField(
        verbose_name=strings.TWITTER_INVITE_SENT,
        default=False
        )

    invite_accepted = models.BooleanField(
        verbose_name=strings.TWITTER_INVITE_ACCEPTED,
        default=False
        )

    class Meta:
        verbose_name = strings.TWITTER_INVITE_VERBOSE_NAME
        verbose_name_plural = strings.TWITTER_INVITE_VERBOSE_NAME_PLURAL
    

class FollowSuggestion(AuditableModel):
    #Falta implementar que no se repitan
    source = models.CharField(
        verbose_name=strings.SUGGESTION_SOURCE,
        max_length=10,
        choices=constants.SUGGESTION_SOURCE_CHOICES
        )

    receiving_user = models.ForeignKey(User,
        verbose_name=strings.WORLDRAT_RECEIVING_USER,
        related_name='follow_suggestions'
        )

    suggested_user = models.ForeignKey(User,
        verbose_name=strings.SUGGESTED_WORLDRAT_USER,
        related_name='suggested_to'
        )

    suggestion_successful = models.BooleanField(
        verbose_name=strings.SUGGESTION_SUCCESSFUL,
        default=False
        )

    class Meta:
        verbose_name = strings.FOLLOW_SUGGESTION_VERBOSE_NAME
        verbose_name_plural = strings.FOLLOW_SUGGESTION_VERBOSE_NAME_PLURAL
