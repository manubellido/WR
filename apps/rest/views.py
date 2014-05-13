# -*- coding: utf-8 -*-

from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import translation
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from rest.http import HttpResponseNoContent
from rest.http import HttpResponseUnauthorized
from rest.auth import AuthenticationResponse
from rest.auth import AuthorizationResponse
from rest import settings as rest_settings


class ResourceView(View):

    additional_http_method_names = ['patch']

    def extend_known_methods(self):
        return []

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Force a language if the settings require it
        if rest_settings.REST_FORCE_LANGUAGE:
            translation.activate(rest_settings.REST_DEFAULT_LANGUAGE)
        # Handling additional HTTP verbs
        for m in self.extend_known_methods():
            if m not in self.additional_http_method_names:
                self.additional_http_method_names.append(m)
        for m in self.additional_http_method_names:
            if m not in self.http_method_names:
                self.http_method_names.append(m)
        # Handling authentication
        response = self.authenticate(request, *args, **kwargs)
        if not response.is_authenticated:
            return self.process_authentication_error(response)
        # Handling authorization
        response = self.authorize(request, *args, **kwargs)
        if not response.is_authorized:
            return self.process_authorization_error(response)
        # Original dispatch logic continues
        return super(ResourceView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def http_method_not_allowed(self, request, *args, **kwargs):
        response = super(ResourceView, self).http_method_not_allowed(
            request, *args, **kwargs
        )
        upcase_methods = [m.upper() for m in self.get_permitted_methods()]
        response['Allow'] = ', '.join(upcase_methods)
        return response

    def get_permitted_methods(self):
        return [m for m in self.http_method_names if hasattr(self, m)]

    def has_documentation(self):
        return hasattr(self, 'documentation')

    def get_documentation(self, attr=None):
        defaults = {
            'url': None,
            'content_type': 'text/html',
            'rel': 'help'
        }
        if self.has_documentation():
            if attr is None:
                return self.documentation
            else:
                try:
                    return self.documentation[attr]
                except KeyError:
                    if attr in defaults:
                        return defaults[attr]
                    else:
                        return None
        else:
            return {}

    def get_documentation_link_value(self, url=None, ctype=None, rel=None):
        url = url or self.get_documentation(attr='url')
        ctype = ctype or self.get_documentation(attr='content_type')
        rel = rel or self.get_documentation(attr='rel')
        if url:
            return '<%s>; type=%s; rel=%s' % (url, ctype, rel, )
        else:
            return None

    def options(self, request, *args, **kwargs):
        response = HttpResponseNoContent()
        upcase_methods = [m.upper() for m in self.get_permitted_methods()]
        response['Allow'] = ', '.join(upcase_methods)
        if self.has_documentation():
            documentation_link = self.get_documentation_link_value()
            if documentation_link is not None:
                response['Link'] = documentation_link
        return response

    def authenticate(self, request, *args, **kwargs):
        response = AuthenticationResponse()
        response.is_authenticated = True
        return response

    def authorize(self, request, *args, **kwargs):
        response = AuthorizationResponse()
        response.is_authorized = True
        return response

    def process_authentication_error(self, auth_response):
        response = HttpResponseUnauthorized(
            content=auth_response.content,
            content_type=auth_response.content_type
        )
        for name, value in auth_response.extra_headers.iteritems():
            response[name] = value
        return response

    def process_authorization_error(self, auth_response):
        response = HttpResponseForbidden(
            content=auth_response.content,
            content_type=auth_response.content_type
        )
        for name, value in auth_response.extra_headers.iteritems():
            response[name] = value
        return response


class CollectionResourceView(ResourceView):
    pass


class FunctionResourceView(ResourceView):

    def get(self, request, *args, **kwargs):
        if hasattr(self, 'run') and callable(self.run):
            return self.run(request, *args, **kwargs)
        else:
            upcase_methods = [m.upper() for m in self.get_permitted_methods()]
            return HttpResponseNotAllowed(upcase_methods)


class ControllerResourceView(ResourceView):

    def post(self, request, *args, **kwargs):
        if hasattr(self, 'run') and callable(self.run):
            return self.run(request, *args, **kwargs)
        else:
            upcase_methods = [m.upper() for m in self.get_permitted_methods()]
            return HttpResponseNotAllowed(upcase_methods)
