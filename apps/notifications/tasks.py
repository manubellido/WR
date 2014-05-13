# -*- coding: utf-8 -*-

from celery.task import task

from django.contrib.auth.models import User
from django.db import transaction

from circuits.models import Circuit
from notifications.models import NotifiableEvent
from notifications.models import Notification
from notifications.constants import NOTIFICATION_TYPE_CHOICES

"""
This is the module that DJcelery will look up for tasks to execute
"""

def process_circuit_created(event):
    """
    Returns a list of users who are doomed to receive the notification
    """
    user = event.owner
    recipients = []
    recipients.extend(user.userprofile.get_followers())
    return recipients
    
def process_circuit_favorited(event):
    """
    Returns a list of users who are doomed to receive the notification
    """
    user = event.owner
    recipients = []
    recipients.extend(user.userprofile.get_followers())
    info = event.make_info_dict()
    try:
        circuit = Circuit.objects.get(pk=int(info['circuit']))
        recipients.append(circuit.author)
    except Circuit.DoesNotExist:
        pass
    
    return recipients   
 
def process_circuit_remixed(event):
    """
    Returns a list of users who are doomed to receive the notification
    """
    user = event.owner
    recipients = []
    recipients.extend(user.userprofile.get_followers())
    info = event.make_info_dict()
    try:
        remixed = Circuit.objects.get(pk=int(info['remixed_circuit']))
        recipients.append(remixed.author)
    except Circuit.DoesNotExist:
        pass
    
    return recipients   

def process_circuit_updated(event):
    """
    Returns a list of users who are doomed to receive the notification
    """
    user = event.owner
    recipients = []
    recipients.extend(user.userprofile.get_followers())
    info = event.make_info_dict()
    try:
        circuit = Circuit.objects.get(pk=int(info['circuit']))
        recipients.extend(circuit.get_followers())
    except Circuit.DoesNotExist:
        pass
    
    return recipients
    
def process_user_followed(event):
    """
    Returns a list of users who are doomed to receive the notification
    """
    recipients = []
    info = envet.make_info_dict()
    try:
        followed = User.objects.get(pk=int(info['followed']))
    except User.DoesNotExist:
        pass
    
    recipients.append(followed)
    return recipients
    
def process_content_shared(event):
    """
    Returns a list of users who are doomed to receive the notification
    """
    pass  


@task
@transaction.commit_on_success
def process_event(event_id):
    """
    processes an event of notification handling the adecuate situation
    of the event type
    """
    # TODO manage logging
    try:
        event = NotifiableEvent.objects.get(pk=event_id)
    except NotifiableEvent.DoesNotExist:
        return
    
    # event.notification_type == NOTIFICATION_TYPE_CHOICES.get_value('CIRCUIT_REMIXED')
    if event.notification_type == 1:
        recipients = process_circuit_created(event)
        
    elif event.notification_type == 2:
        recipients = process_circuit_favorited(event)
        
    elif event.notification_type == 3:
        recipients = process_circuit_remixed(event)
    
    elif event.notification_type == 4:
        recipients = process_circuit_updated(event)
        
    elif event.notification_type == 5:
        recipients = process_user_followed(event)
        
    else:
        recipients = process_content_shared(event)
        
    for user in recipients:
        event.create_notification(user)
        
    event.mark_as_processed()
    

