# -*- coding: utf-8 -*-

from django import template

from circuits.constants import CIRCUIT_CATEGORY_CHOICES
from circuits.models import CircuitRelatedUserProxy
from circuits.utils import CircuitCategory


register = template.Library()

@register.assignment_tag(takes_context=True)
def get_cats(context):
    result = {}
    request = context['request']
    # Grab category objects
    if request.user.is_authenticated():
        uproxy = CircuitRelatedUserProxy.from_user(request.user)
        fav_cats = uproxy.get_favorite_circuit_categories()
        non_fav_cats = uproxy.get_non_favorite_circuit_categories()
    else:
        fav_cats = []
        non_fav_cats = []
        for c in CIRCUIT_CATEGORY_CHOICES:
            non_fav_cats.append(CircuitCategory(c[0]))

    # TODO: Sort each list of objects by name asc
    # Build result dictionary
    fav_cats.sort(cmp=lambda x,y: cmp(unicode(x.description.lower()),
                                      unicode(y.description.lower())))
    non_fav_cats.sort(cmp=lambda x,y: cmp(unicode(x.description.lower()),
                                          unicode(y.description.lower())))
    result['favorites'] = fav_cats
    result['non_favorites'] = non_fav_cats
    # Return result
    return result
