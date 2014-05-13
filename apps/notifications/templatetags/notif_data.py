from django import template
from django.contrib.auth.models import User

from notifications.models import Notification
from circuits.models import Circuit
from places.models import Place

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_notification_data(context, notification):
    result = notification.get_info_dict()
    if notification_type == 1:
        result['author'] = User.objects.get(id=result['author'])
        result['circuit'] = Circuit.objects.get(id=result['circuit'])
    elif notification_type == 2:
        result['user_favoriting'] =\
            User.objects.get(id=result['user_favoriting'])
        result['circuit'] = Circuit.objects.get(id=result['circuit'])
    elif notification_type == 3:
        result['user_favoriting'] =\
            User.objects.get(id=result['user_favoriting'])
        result['circuit'] = Circuit.objects.get(id=result['circuit'])
    elif notification_type == 4:
        result['remixed_circuit'] =\
            Circuit.objects.get(id=result['remixed_circuit'])
        result['original_circuit'] =\
            Circuit.objects.get(id=result['original_circuit'])
    elif notification_type == 5:
        result['circuit'] = Circuit.objects.get(id=result['circuit'])
        result['place'] = Place.objects.get(id=result['place'])
    elif notification_type == 6:
        result['follower'] = User.objects.get(id=result['follower'])
    return result
