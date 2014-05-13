# -*- coding: utf-8 -*-

import re
from django.conf import settings
from django.shortcuts import redirect
from user_profile.models import UserProfile

class SetLanguage(object):

    def process_request(self, request):
        if hasattr(request, 'user'):
            # FIXME: kinda hacky the way it determines user preference
            if request.user.is_anonymous():
                if request.COOKIES.has_key('django_language'):
                    request.session['django_language'] = \
                        request.COOKIES['django_language']
                if request.COOKIES.has_key('verbose_language'):
                    request.session['verbose_language'] = \
                        request.COOKIES['verbose_language']
                else:
                    verbose_language = None
                    for language in settings.LANGUAGES:
                        if request.LANGUAGE_CODE == language[0]:
                            verbose_language = language[1]
                            break
                    #Need something here in case of wrong language
                    #code
                    request.session['verbose_language'] = verbose_language
            else:
                try:
                    pref_lang = request.user.userprofile.language - 1
                    pref_lang_str = settings.LANGUAGES[pref_lang][0]
                    pref_lang_verbose = settings.LANGUAGES[pref_lang][1]
                    if hasattr(request, 'session'):
                        request.session['django_language'] = pref_lang_str
                        request.session['verbose_language'] = pref_lang_verbose
                except:
                    return None
        return None
