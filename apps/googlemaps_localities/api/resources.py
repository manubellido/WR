#! -*- coding: utf-8 -*-

import django.utils.simplejson as json

from ordereddict import OrderedDict
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.conf import settings
from rest.views import ControllerResourceView
from rest.views import CollectionResourceView
from rest.views import FunctionResourceView
from rest.http import HttpResponseConflict
from rest.auth import RESTfulBasicOrDjangoAuthenticationMixIn as AuthMixIn
from rest.utils import render_as_json
from rest.utils import json_error_document
from rest.utils import error_list_from_form
from googlemaps_localities.api.forms import LatLngValidationForm
from googlemaps_localities import strings, constants
from googlemaps_localities.models import GoogleMapsAddressComponent as GMAC

class GMACLookupController(
    AuthMixIn,
    ControllerResourceView
):
    """
    RESP API, returns the associated GMAC for a given list of GMAC 
    objects as JSON obtained by calling the reverse geocoding API 
    from Google Maps.
    """
    def run(self, request, *args, **kwargs):

        if len(request.body) > 0:
            # Parse data
            try:
                data = json.loads(request.body)
            except Exception:
                error = OrderedDict()
                message = strings.GMAC_JSON_NOT_PARSED
                error['message'] = unicode(message)
                error_list = [error]
                return HttpResponse(
                    content=json_error_document(error_list),
                    content_type='application/json'
                )

            # Grab an address component
            gmac = GMAC.get_or_create_locality_from_json(request.body)

            if gmac is not None:

                # Build response
                document = OrderedDict()
                document['gmac_id'] = gmac.pk
                return HttpResponse(
                    content=render_as_json(document),
                    content_type='application/json'
                )

            else:
                error = OrderedDict()
                message = strings.GMAC_NOT_FOUND
                error['message'] = unicode(message)
                error_list = [error]
                return HttpResponse(
                    content=json_error_document(error_list),
                    content_type='application/json'
                )

        else:
            # Bad Request
            error = OrderedDict()
            message = strings.GMAC_LIST_MISSING
            error['message'] = unicode(message)
            error_list = [error]
            return HttpResponseBadRequest(
                content=json_error_document(error_list),
                content_type='application/json'
            )


class GMACLookupByCoordsFunction(
    AuthMixIn,
    FunctionResourceView
):
    """
    RESP API, returns the associated GMAC for a given pair of coordinates
    """
    def run(self, request, *args, **kwargs):

        form = LatLngValidationForm(request.GET)

        # Bad Request
        if not form.is_valid():
            error_list = error_list_from_form(form, prefix_with_fields=False)
            return HttpResponseBadRequest(
                content=json_error_document(error_list),
                content_type='application/json'
            )

        # FIXME: Implementation pending

        # Build response
        document = OrderedDict()
        return HttpResponse(
            content=render_as_json(document),
            content_type='application/json'
        )
