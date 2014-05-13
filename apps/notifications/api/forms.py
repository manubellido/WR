#! -*- coding: utf-8 -*-

from ordereddict import OrderedDict
from django import forms
from common.utils.strings import multiple_whitespace_to_single_space

from notifications.models import Notification
from notifications import constants

class NotificationCollectionFilterForm(forms.Form):
    """
    Validates the fields limit and offset or catches them from constants
    """

    limit = forms.IntegerField(
        min_value=1,
        required=False
    )

    offset = forms.IntegerField(
        min_value=0,
        required=False
    )

    def get_notifications(self, user):
        """
        Returns a Queryset of notifications
        """
        limit = self.cleaned_data.get('limit', None)
        offset = self.cleaned_data.get('offset', None)

        # set defaults if limit and offset dont come
        if limit is None:
            limit = constants.API_DEFAULT_NOTIFICATIONS_LIMIT
        if offset is None:
            offset = constants.API_DEFAULT_NOTIFICATIONS_OFFSET

        notifications = Notification.objects.order_by('-created')

        return notifications[offset:offset + limit]
