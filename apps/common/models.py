# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from common.middleware import threadlocals

class AuditableManager(models.GeoManager):
    """
    Replacement for the default manager in AuditableModels so we only query
    for the active objects.
    """
    pass


class AuditableModel(models.Model):
    """
    AuditableModel inherits from models.Model and implements the following
    fields for audit purposes:
      * uuid
      * created
      * modified
      * created_by
      * modified_by
    """

    uuid = models.CharField(
        max_length=36,
        unique=True,
        editable=False
    )

    created = models.DateTimeField(
        verbose_name=_('Creado'),
        auto_now_add=True,
        editable=False
    )

    modified = models.DateTimeField(
        verbose_name=_('Modificado'),
        auto_now=True,
        null=True,
        editable=False
    )

    created_by = models.ForeignKey(User,
        verbose_name=_('Creado por'),
        related_name="%(class)s_related",
        editable=False
    )

    modified_by = models.ForeignKey(User,
        verbose_name=_('Modificado por'),
        related_name="%(class)s_related_mod",
        null=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        """
        If its a new object, set the creation user and assign the url_id
        """
        # If the object already existed, it will already have an id
        if self.id:
            user = threadlocals.get_non_anonymous_user()
            # This object is being edited, not saved, set last_edited_by
            self.modified_by = threadlocals.get_non_anonymous_user()
        else:
            # This is a new object, set the owner
            self.created_by = threadlocals.get_non_anonymous_user()
            self.uuid = uuid4()
            # Save first to obtain an ID
            super(AuditableModel, self).save(*args, **kwargs)
            kwargs['force_insert'] = False

        # Check is url_id exist, if not, generate to save
        if not self.uuid:
            self.uuid = uuid4()

        super(AuditableModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
