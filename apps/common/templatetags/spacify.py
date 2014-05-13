# -*- coding: utf-8 -*-

from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
import re

register = Library()

@register.filter(name='spacify', needs_autoescape=True)
@stringfilter
def spacify(value, autoescape=None):
    """
    Taken from: http://stackoverflow.com/questions/721035/django-templates-stripping-spaces
    """
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    return mark_safe(re.sub('\s', '&'+'nbsp;', esc(value)))
