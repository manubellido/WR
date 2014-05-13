# -*- coding: utf-8 -*-
from django.contrib.gis.db import models

from redirections import strings


class Redirection(models.Model):
    """Model class definition for a Redirection"""

    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name=strings.NAME_VERBOSE,
    )

    path = models.CharField(
        max_length=200,
        blank=False,
        verbose_name=strings.PATH_VERBOSE_NAME,
    )

    redirect_to = models.URLField(
        blank=False,
        verbose_name=strings.REDIRECT_TO_VERBOSE_NAME,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = strings.REDIRECTION_VERBOSE_NAME
        verbose_name_plural = strings.REDIRECTION_VERBOSE_NAME_PLURAL
