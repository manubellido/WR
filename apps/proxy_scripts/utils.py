# -*- coding: utf-8 -*-

from random import choice
from urllib import urlencode
from django.conf import settings

def pick_random_proxy(proxy_list=None):
    if proxy_list is None:
        proxy_list = settings.PROXY_SCRIPTS
        return choice(proxy_list)
    else:
        return None

def generate_proxied_url(target_url, proxy_url=None):
    if proxy_url is None:
        proxy_url = pick_random_proxy()
    return "%s?%s" % (
        proxy_url,
        urlencode({'url':target_url})
    )
