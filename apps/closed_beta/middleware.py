# -*- coding: utf-8 -*-

import re
from django.conf import settings
from django.shortcuts import redirect

class InvitationRequired(object):

    def process_response(self, request, response):

        if not settings.CLOSED_BETA_ACTIVE:
            return response

        if (hasattr(request, 'user')
                and hasattr(request.user, 'is_authenticated')
                and request.user.is_authenticated()):
            return response
        elif (request.path in
                settings.CLOSED_BETA_INVITATION_MIDDLEWARE_EXCEPTED_URIS):
            return response
        elif response.status_code < 200 or response.status_code >= 300:
            return response
        else:
            for regex in \
                settings.CLOSED_BETA_INVITATION_MIDDLEWARE_EXCEPTED_PATTERNS:
                if re.compile(regex).match(request.path):
                    return response

        return redirect(settings.CLOSED_BETA_INVITATION_MIDDLEWARE_REDIRECT)
