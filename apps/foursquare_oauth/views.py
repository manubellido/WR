# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.simple import direct_to_template
from django.views.decorators.cache import never_cache
from django.utils.cache import patch_vary_headers
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings

from foursquare_oauth.integration import FoursquareIntegrator
from user_profile.registration.utils import get_redirect_uri
from user_profile.models import UserFacebook
from user_profile.utils import \
    psv_get, psv_set, psv_exists, psv_save, psv_restore


@never_cache
def foursquare_authorization(request):
    # Register expected optional parameters
    params = ('client_id', 'redirect_uri', )
    for p in params:
        v = request.GET.get(p, None)
        if v is not None:
            psv_set(request, 'registration_' + p, v)
    # Start authorization request
    integrator = FoursquareIntegrator()
    redirect_uri = integrator.get_full_registration_end_url()
    authorization_uri = integrator.create_authorization_url(redirect_uri)
    print authorization_uri
    return HttpResponseRedirect(authorization_uri)

@never_cache
def foursquare_authorization_redirection_end(request):
    integrator = FoursquareIntegrator()
    if 'code' in request.GET:
        code = request.GET.get('code')
        redirect_uri = integrator.get_full_registration_end_url()
        access_token = integrator.get_access_token(redirect_uri, code)
    else:
        access_token = None
    if access_token is not None:
        psv_set(request, 'foursquare_access_token', access_token)
        integrator.add_foursquare_user_record(access_token, request.user)
        return redirect('show_user_profile', request.user.id)

    psv_restore(request, temp_dict)
    # TODO: fix this, in case url returns without an oauth code, which
    # shouldn't happen anyway.
    return HttpResponseRedirect(integrator.get_registration_form_url())

