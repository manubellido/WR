# -*- coding: utf-8 -*-

from django import template
from places.models import DonePlace

register = template.Library()

@register.simple_tag
def done_places(user, circuit):
    places = circuit.get_places()
    visited = DonePlace.objects.filter(place__in=places)\
            .filter(user=user).count()
    if visited == 0:
        return ''
    return str(visited)