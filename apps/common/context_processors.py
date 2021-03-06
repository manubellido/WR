# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site

def current_site(request):
    return {
        'CURRENT_SITE': Site.objects.get_current().domain,
        'SETTINGS': settings,
    }
        

