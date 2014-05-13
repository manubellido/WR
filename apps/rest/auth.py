# -*- coding: utf-8 -*-

from ordereddict import OrderedDict
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from rest.utils import json_error_document

def check_django_authentication(request):
    return request.user.is_authenticated()

def check_http_basic_authentication(request):
    if request.META.has_key('HTTP_AUTHORIZATION'):
        authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
        if authmeth.lower() == 'basic':
            auth = auth.strip().decode('base64')
            username, password = auth.split(':', 1)
            user = authenticate(username=username, password=password)
            if user is not None:
                request.user = user
                return True
    # Any of the other if statements fails...
    request.user = AnonymousUser()
    return False

class AuthenticationResponse(object):

    def __init__(self, content=None, content_type=None):
        self.content = content
        self.is_authenticated = False
        self.extra_headers = OrderedDict()
        self.content_type = content_type
        #FIXME: Return a default HTML page if no other content present
        super(AuthenticationResponse, self).__init__()


class AuthorizationResponse(object):

    def __init__(self, content=None, content_type=None):
        self.content = content
        self.is_authorized = False
        self.extra_headers = OrderedDict()
        self.content_type = content_type
        #FIXME: Return a default HTML page if no other content present
        super(AuthorizationResponse, self).__init__()


class RESTfulDjangoAuthenticationMixIn(object):

    def authenticate(self, request, *args, **kwargs):

        response = AuthenticationResponse()

        if check_django_authentication(request):
            response.is_authenticated = True
        else:
            message  = u'A Django session must have been started '
            message += u'before using this web service API.'
            errors = [{'message': message}]
            response.content = json_error_document(errors)
            response.is_authenticated = False
            response.content_type = 'application/json'

        return response


class RESTfulBasicAuthenticationMixIn(object):

    def authenticate(self, request, *args, **kwargs):

        response = AuthenticationResponse()

        if check_http_basic_authentication(request):
            response.is_authenticated = True
        else:
            message  = u'A valid pair of credentials must be sent with '
            message += u'the request using HTTP Basic Authentication '
            message += u'before using this web service API.'
            errors = [{'message': message}]
            response.content = json_error_document(errors)
            response.is_authenticated = False
            response.content_type = 'application/json'

        return response
    

class RESTfulBasicOrDjangoAuthenticationMixIn(object):

    def authenticate(self, request, *args, **kwargs):

        response = AuthenticationResponse()

        if check_django_authentication(request):
            response.is_authenticated = True
        elif check_http_basic_authentication(request):
            response.is_authenticated = True
        else:
            message  = u'A Django session must have been started '
            message += u'or valid credentials must have been sent '
            message += u'using HTTP Basic Authentication before using '
            message += u'this web service API.'
            errors = [{'message': message}]
            response.content = json_error_document(errors)
            response.is_authenticated = False
            response.content_type = 'application/json'

        return response
