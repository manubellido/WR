# -*- coding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def active(request, view_name, *args, **kwargs):
    if request.path == reverse(view_name, args=args, kwargs=kwargs):
        return 'active'
