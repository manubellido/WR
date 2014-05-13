# -*- coding: utf-8 -*-
from django import http

from redirections.models import Redirection


class RedirectionMiddleware(object):
    def process_response(self, request, response):
        path = request.path
        if path[-1] == '/':
            path = path[:-1]
        try:
            redirect_to = Redirection.objects.get(path=path).redirect_to
            return http.HttpResponsePermanentRedirect(redirect_to)
        except Redirection.DoesNotExist:
            pass
        return response
