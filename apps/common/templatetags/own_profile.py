# -*- coding: utf-8 -*-

from django import template


@register.simeple_tag
def is_own_profile(request, wr_user):
    """
    Intended use
    {% if is_own_profile request wr_user %}
      stuff goes here
    {% endif %}

    Figure out a way to be {% is_own_profile request wr_user %}
    """
    if request.user.is_authenticated():
        if request.user == wr_user:
            return 'True'
        else:
            return ''
    else:
        return ''
