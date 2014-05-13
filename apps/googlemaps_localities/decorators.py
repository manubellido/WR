# -*- coding: utf-8 -*-

from common.utils.match_gmac import match_gmac
from googlemaps_localities.models import GoogleMapsAddressComponent

def set_gmac_in_session(request, ip):
    gmac = match_gmac(str(ip))
    if gmac is not None:
        request.session['gmac_ipaddr'] = request.META['REMOTE_ADDR']
        request.session['gmac_id'] = gmac.pk
        request.gmac=gmac

def set_gmac(func):
    """
    decorator for adding gmac to a request session
    """
    def auxiliar(request, *args, **kwargs):
        ip = request.META['REMOTE_ADDR']
        session_ip = request.session.get('gmac_ipaddr', None)
        if session_ip is None:
            set_gmac_in_session(request, ip)
        elif str(session_ip) != str(ip):
            set_gmac_in_session(request, ip)
        else:
            if not hasattr(request, 'gmac'):
                gmac = match_gmac(str(ip))
                request.gmac = gmac

        return func(request, *args, **kwargs)

    return auxiliar

