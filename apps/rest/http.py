# -*- coding: utf-8 -*-

from django.http import HttpResponse


class HttpResponseCreated(HttpResponse):                                      
    status_code = 201

class HttpResponseNoContent(HttpResponse):                                      
    status_code = 204

    def __init__(self, content='', mimetype=None, status=None, 
            content_type=None):
        return super(HttpResponseNoContent, self).__init__(
            content='', 
            mimetype=mimetype,
            status=None, 
            content_type=content_type
        )

class HttpResponseSeeOther(HttpResponse):
    status_code = 303

class HttpResponseUnauthorized(HttpResponse):
    status_code = 401

class HttpResponseNotAcceptable(HttpResponse):
    status_code = 406

class HttpResponseConflict(HttpResponse):
    status_code = 409


