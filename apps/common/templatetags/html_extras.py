#! -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def keeptags(value, tags):
    """Strigs all [X]HTML tags except the listed ones"""
    from common.utils.html import keeptags as ktutil
    return mark_safe(ktutil(value, tags))
keeptags.is_safe = True

@register.filter
@stringfilter
def ratio_hw(value):
    return value.height / value.width


@register.filter
@stringfilter
def twitterize(value):
    """Converts words starting with @ into hrefs pointing to Twitter."""
    words = value.split()
    href = '<a href="https://twitter.com/%s" rel="nofollow">%s</a>'
    hashtag_href = '<a href="/search/?q=%%23%s" rel="nofollow">%s</a>'

    for i in range(len(words)):
        if words[i][0] == '@':
            words[i] = href % (words[i][1:], words[i])

        if words[i][0] == '#':
            words[i] = hashtag_href % (words[i][1:], words[i])
        
    return mark_safe(u' '.join(words))

