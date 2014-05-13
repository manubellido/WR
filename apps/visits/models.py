# -*- coding: utf-8 -*-

from pygeoip import GeoIP
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

from common.models import AuditableModel
from visits import strings


class Visit(AuditableModel):

    visitor = models.ForeignKey(User,
        verbose_name=strings.VISIT_VISITOR,
        related_name='visits',
        null=True,
        blank=True
    )

    visitor_ip = models.IPAddressField(
        verbose_name=strings.VISIT_IP_ADDRESS,
        null=True,
        blank=True
    )

    country_code = models.CharField(
        verbose_name=strings.VISIT_COUNTRY_CODE,
        max_length=2,
        null=True,
        blank=True
    )

    user_agent = models.CharField(
        verbose_name=strings.VISIT_USER_AGENT,
        max_length=256,
        null=True,
        blank=True
    )

    # Generic FK to any other model, Circuit, Place, etc...
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(
        'content_type', 'object_id'
    )
            
    def __unicode__(self):
        return self.visitor_ip

    def update_data(self, request, commit=True):
        self.user_agent = request.META.get('HTTP_USER_AGENT', None)
        geo = GeoIP(settings.GEOIP_DATABASE)
        self.country_code = geo.country_code_by_addr(
            request.META.get('REMOTE_ADDR', None)
        )
        self.visitor_ip = request.META.get('REMOTE_ADDR', None)
        if hasattr(request, 'user') and request.user.is_authenticated():
            self.visitor = request.user
        if commit:
            self.save()

    class Meta:
        verbose_name = strings.VISIT_VERBOSE_NAME
        verbose_name_plural = strings.VISIT_VERBOSE_NAME_PLURAL

    @staticmethod
    def create_visit(request, content_object):
        visit = Visit(content_object=content_object)
        visit.update_data(request)
