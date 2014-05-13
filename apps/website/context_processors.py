# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse


def login_link_flag(request):
    flag = not (request.path == reverse('auth_login'))
    return {'display_login_link': flag}


def registration_link_flag(request):
    flag = not (request.path == reverse('registration_register'))
    return {'display_registration_link': flag}
