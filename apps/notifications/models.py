# -*- coding: utf-8 -*-

import json
import datetime
from ordereddict import OrderedDict

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives

from common.models import AuditableModel
from notifications import strings, constants
from circuits.models import Circuit
from rest.utils import render_as_json

class NotifiableEvent(AuditableModel):

    owner = models.ForeignKey(User,
        verbose_name=strings.NOTIFIABLE_EVENT_OWNER
    )

    notification_type = models.PositiveIntegerField(
        verbose_name=strings.NOTIFIABLE_EVENT_NOTIFICATION_TYPE,
        choices=constants.NOTIFICATION_TYPE_CHOICES
    )

    info = models.TextField(
        verbose_name=strings.NOTIFIABLE_EVENT_INFO
    )

    processed = models.BooleanField(
        verbose_name=strings.NOTIFIABLE_EVENT_PROCESSED,
        default=False
    )

    processed_at = models.DateTimeField(
        verbose_name=strings.NOTIFIABLE_EVENT_PROCESSED_AT,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = strings.NOTIFIABLE_EVENT_VERBOSE_NAME
        verbose_name_plural = strings.NOTIFIABLE_EVENT_VERBOSE_NAME_PLURAL

    def register(self):
        from notifications.tasks import process_event
        # Sending task to Celery backend
        process_event.apply_async(
            kwargs={
                'event_id': self.pk
            }, 
            serializer="json"
        ) 

    def mark_as_processed(self):
        self.processed = True
        self.processed_at = datetime.datetime.now()
        self.save()

    def create_notification(self, user):
        notification = Notification()
        notification.notified_user=user
        notification.info=self.info
        notification.notification_type = self.notification_type
        notification.save()
        return notification
     
    def make_info_dict(self):
        return json.loads(self.info)
    
    @staticmethod
    def register_event_circuit_created(owner, circuit, timestamp=None):

        metadata = {
            'author': circuit.author.id,
            'circuit': circuit.id,
        }

        nt = constants.NOTIFICATION_TYPE_CHOICES.CIRCUIT_CREATED

        event = NotifiableEvent(
            owner=owner,
            notification_type=nt,
        )
        
        if timestamp is None:
            timestamp = datetime.datetime.now()

        metadata['timestamp'] = unicode(timestamp)

        event.info = render_as_json(metadata)
        event.save()
        event.register()
        return event

    @staticmethod
    def register_event_circuit_favorited(
        owner,
        circuit,
        timestamp=None
    ):
        metadata = {
            'user': owner.id,
            'circuit': circuit.id,
        }

        nt = constants.NOTIFICATION_TYPE_CHOICES.CIRCUIT_FAVORITED

        event = NotifiableEvent(
            owner=owner,
            notification_type=nt
        )

        if timestamp is None:
            timestamp = datetime.datetime.now()

        metadata['timestamp'] = unicode(timestamp)

        event.info = render_as_json(metadata)
        event.save()
        event.register()
        return event

    @staticmethod
    def register_event_circuit_remixed(
            owner,
            remixed_circuit,
            original_circuit,
            timestamp=None
        ):
            
        metadata = {
            'user' : owner.pk,
            'remixed_circuit': remixed_circuit.id,
            'original_circuit': original_circuit.id,
        }
        
        nt = constants.NOTIFICATION_TYPE_CHOICES.CIRCUIT_REMIXED

        event = NotifiableEvent(
            owner=owner,
            notification_type=nt,
        )
        
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        metadata['timestamp'] = unicode(timestamp)

        event.info = render_as_json(metadata)
        event.save()
        event.register()
        return event

    @staticmethod
    def register_event_circuit_updated(
            owner,
            circuit,
            timestamp=None
        ):
        
        metadata = {
            'circuit': circuit.id,
        }
        
        nt = constants.NOTIFICATION_TYPE_CHOICES.CIRCUIT_UPDATED

        event = NotifiableEvent(
            owner=owner,
            notification_type=nt,
        )
        
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        metadata['timestamp'] = unicode(timestamp)

        event.info = render_as_json(metadata)
        event.save()
        event.register()
        return event

    @staticmethod
    def register_event_user_followed(
            owner,
            followed,
            timestamp=None
        ):
        
        metadata = {
            'follower' : owner.id,
            'followed': followed.id,
        }

        nt = constants.NOTIFICATION_TYPE_CHOICES.USER_FOLLOWED

        event = NotifiableEvent(
            owner=owner,
            notification_type=nt,
        )
        
        if timestamp is None:
            timestamp = datetime.datetime.now()
            
        metadata['timestamp'] = unicode(timestamp)

        event.info = render_as_json(metadata)
        event.save()
        event.register()
        return event

    @staticmethod
    def register_event_content_shared():
        #FIXME: Implementation pending
        pass


class Notification(AuditableModel):

    notified_user = models.ForeignKey(User,
        verbose_name=strings.NOTIFIED_USER,
        related_name='notifications'
    )

    notification_type = models.PositiveIntegerField(
        verbose_name=strings.NOTIFICATION_TYPE,
        choices=constants.NOTIFICATION_TYPE_CHOICES
    )

    info = models.TextField(
        verbose_name=strings.NOTIFICATION_INFO
    )

    displayed = models.BooleanField(
        verbose_name=strings.NOTIFICATION_DISPLAYED,
        default=False
    )

    class Meta:
        verbose_name = strings.NOTIFICATION_VERBOSE_NAME
        verbose_name_plural = strings.NOTIFICATION_VERBOSE_NAME_PLURAL

    def save(self):
        """Parent save method, here the mails are sent"""
        super(Notification, self).save()
        # get user recipent
        us = self.notified_user
        # check that user has a valid email address
        if us.email.find('@') > 0 and us.email.find('.') > 0:
            # mandatory fields
            subject = strings.EMAIL_NOTIFICATION_SUBJECT
            to =  us.email
            from_email = settings.DEFAULT_FROM_EMAIL
            # get text version of the message
            text_content = self.get_email_content_from_type(
                self.notification_type
            )
            # FIXME: HTML version implementation pending
            html_content = self.get_email_content_from_type(
                self.notification_type
            )
            msg = EmailMultiAlternatives(
                subject, 
                text_content,
                from_email,
                [to]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    def get_email_content_from_type(self, type):
        """Returns the content of the mail according to the not_type"""
        if type is 1:
            return strings.CIRCUIT_CREATED_EMAIL_NOTIFICATION
        # case circuit is favorited
        if type is 2:
            # parse the route from info textfield
            route = self.info[self.info.find('circuit'):]
            route = route[:route.find('\n')]
            route = route[route.find(':')+2:]
            try:
                circuit = Circuit.objects.get(pk=route)
                circuit_name = circuit.name
            except Circuit.DoesNotExist:
                circuit_name = 'Route :)'
            # parse the user from info textfield
            us = self.info[self.info.find('user')+7:]
            us = us[:us.find(',')]
            try:
                user = User.objects.get(pk=us)
                user = user.get_full_name()
            except User.DoesNotExist:
                user = 'Some Worldrat user :)'
            return strings.CIRCUIT_FAVORITED_EMAIL_NOTIFICATION % {
                'route':circuit_name, 'user': user,
            }

        if type is 3:
            # parse the route from info textfield
            route = self.info[self.info.find('original_circuit')+19:]
            route = route[:route.find(',')]
            try:
                circuit = Circuit.objects.get(pk=route)
                circuit_name = circuit.name
            except Circuit.DoesNotExist:
                circuit_name = 'Route :)'
            # parse the user from info textfield
            us = self.info[self.info.find('user')+7:]
            us = us[:us.find(',')]
            try:
                user = User.objects.get(pk=us)
                user = user.get_full_name()
            except User.DoesNotExist:
                user = 'Some Worldrat user :)'
            return strings.CIRCUIT_REMIXED_EMAIL_NOTIFICATION % {
                'route':circuit_name, 'user': user,    
            }
        if type is 4:
            return strings.CIRCUIT_UPDATED_EMAIL_NOTIFICATION
        if type is 5:
            return strings.USER_FOLLOWED_EMAIL_NOTIFICATION
        if type is 6:
            return strings.CONTENT_SHARED_EMAIL_NOTIFICATION

    def get_html_email_content_from_type(self, type):
        """Returns the content of the mail according to the not_type
        in html form"""
        # WORK IN PROGRESS
        
        template = 'mails/notification.html'

        context_dict = {}
        context_dict['notified_user'] = self.notified_user
        context_dict['type'] = type

        info_dict = json.loads(self.info)

        if type is 1:
            try:
                author = User.objects.get(pk=info_dict['author'])
            except User.DoesNotExist:
                author = None

            try:
                circuit = Circuit.objects.get(pk=info_dict['circuit'])
            except Circuit.DoesNotExist:
                circuit = None

            context_dict['circuit'] = circuit
            context_dict['notification_msg'] = \
                strings.CIRCUIT_CREATED_EMAIL_NOTIFICATION
        # case circuit is favorited
        if type is 2:
            try:
                circuit = Circuit.objects.get(pk=info_dict['circuit'])
            except Circuit.DoesNotExist:
                circuit = None

            try:
                user = User.objects.get(pk=info_dict['user'])
            except User.DoesNotExist:
                user = None

            return strings.CIRCUIT_FAVORITED_EMAIL_NOTIFICATION % {
                'route':circuit_name, 'user': user,
            }

        if type is 3:
            # parse the route from info textfield
            route = self.info[self.info.find('original_circuit')+19:]
            route = route[:route.find(',')]
            try:
                circuit = Circuit.objects.get(pk=route)
                circuit_name = circuit.name
            except Circuit.DoesNotExist:
                circuit_name = 'Route :)'
            # parse the user from info textfield
            us = self.info[self.info.find('user')+7:]
            us = us[:us.find(',')]
            try:
                user = User.objects.get(pk=us)
                user = user.get_full_name()
            except User.DoesNotExist:
                user = 'Some Worldrat user :)'
            return strings.CIRCUIT_REMIXED_EMAIL_NOTIFICATION % {
                'route':circuit_name, 'user': user,    
            }
        if type is 4:
            return strings.CIRCUIT_UPDATED_EMAIL_NOTIFICATION
        if type is 5:
            return strings.USER_FOLLOWED_EMAIL_NOTIFICATION
        if type is 6:
            return strings.CONTENT_SHARED_EMAIL_NOTIFICATION

    def make_info_dict(self):
        return json.loads(self.info)

    def get_restful_url(self):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('notification_resource', 
            kwargs={'notification_id': self.id})
        )

    def get_restful_link_metadata(self):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = 'alternate'
        metadata['title'] = self.notification_type
        metadata['type'] = 'application/json'
        return metadata

    @staticmethod
    def get_notifications(user):
        return self.objects.filter(notified_user=user)
