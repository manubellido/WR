# -*- coding: utf-8 -*-
"""
Authorization code in Circuit's REST API
"""

from ordereddict import OrderedDict
from rest.auth import AuthorizationResponse
from circuits.models import Circuit
from circuits import strings
from rest.utils import json_error_document


class BaseCircuitAuthorizationMixIn(object):

    def authorize(self, request, *args, **kwargs):
        response = AuthorizationResponse()
        circuit_id = self.get_circuit_id(request, *args, **kwargs)
        if circuit_id > 1:
            try:
                circuit = Circuit.objects.get(pk=circuit_id)
                if not circuit.is_authorized(request.user):
                    error = OrderedDict()
                    error['message'] = unicode(
                        strings.UNAUTHORIZED_CIRCUIT_EDIT
                    )
                    error_list = [error]
                    response.is_authorized = False
                    response.content = json_error_document(error_list)
                    response.content_type = 'application/json'
                else:
                    response.is_authorized = True
            except Circuit.DoesNotExist:
                # Let the form handle the missing circuit
                response.is_authorized = True
        else:
            # Let the form handle the invalid circuit id
            response.is_authorized = True
        # Return authorization response
        return response

class KwargsCircuitAuthorizationMixIn(BaseCircuitAuthorizationMixIn):

    def get_circuit_id(self, request, *args, **kwargs):
        return kwargs.get('circuit_id', 0)


class PostCircuitAuthorizationMixIn(BaseCircuitAuthorizationMixIn):

    def get_circuit_id(self, request, *args, **kwargs):
        return request.POST.get('circuit_id', 0)

