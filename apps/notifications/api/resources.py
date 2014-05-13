#! -*- coding: utf-8 -*-

from ordereddict import OrderedDict

from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from rest.http import HttpResponseCreated
from rest.http import HttpResponseConflict
from rest.http import HttpResponseSeeOther

from rest.views import ResourceView
from rest.views import CollectionResourceView
from rest.views import FunctionResourceView
from rest.views import ControllerResourceView

from rest.utils import render_as_json
from rest.utils import json_error_document
from rest.utils import error_list_from_form
from rest.auth import RESTfulBasicOrDjangoAuthenticationMixIn
from rest.auth import AuthorizationResponse

from notifications import strings
from notifications.models import Notification
from notifications.api.forms import NotificationCollectionFilterForm


class NotificationResource(ResourceView):
    """
    Notification by itself
    """
    def get(self, request, *args, **kwargs):
        notification_id = kwargs.get('notification_id', 0)
        try:
            notification = Notification.objects.get(pk=notification_id)
            json_document = NotificationResource.json_representation(
                notification
            )
            return HttpResponse(json_document)

        except Notification.DoesNotExist:
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_NOTIFICATION)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

    @staticmethod
    def json_representation(notification, render_json=True):
        document = OrderedDict()
        document['id'] = notification.pk
        document['notification_type'] = notification.notification_type
        try:
            document['notified_user'] = \
                notification.notified_user.userprofile.get_restful_link_metadata()
        except UserProfile.DoesNotExist:
            document['notified_user'] = None
        document['info'] = notification.make_info_dict()

        if render_json:
            return render_as_json(document)
        else:
            return document
            

class UserNotificationCollection(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    CollectionResourceView
):
    """
    Collection of notifications for single user
    """
    
    def get(self, request, *args, **kwargs):
        """
        Returns a collection of notifications with an offset
        and a limit
        """
        # get user
        user = request.user
        
        form = NotificationCollectionFilterForm(request.GET)
        if form.is_valid():
            document = OrderedDict()
            document['link'] = self.get_restful_link_metadata(user,rel='self')
            document['notifications'] = []
            # get notifications from Form
            notifications = form.get_notifications(user)
            # append each notification metadata to a list
            for nt in notifications:
                document['notifications'].append(nt.get_restful_link_metadata())

            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
             )   
             
    def get_restful_url(self, user):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('notification_collection_resource',
                kwargs = { 'user_id': user.pk})
        )

    def get_restful_link_metadata(self, user, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url(user)
        metadata['rel'] = rel
        metadata['title'] = unicode(strings.NOTIFICATION_COLLECTION_NAME)
        metadata['type'] = 'application/json'
        return metadata

    
    
    
