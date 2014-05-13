# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.simple import direct_to_template
from django.views.decorators.cache import never_cache
from django.utils.cache import patch_vary_headers
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.conf import settings

from twitter.integration import TwitterIntegrator
from user_profile.registration.utils import get_redirect_uri
from user_profile.utils import \
    psv_get, psv_set, psv_exists, psv_save, psv_restore


@never_cache
def twitter_authorization(request):
    # Register expected optional parameters
    params = ('client_id', 'redirect_uri', )
    for p in params:
        v = request.GET.get(p, None)
        if v is not None:
            psv_set(request, 'registration_' + p, v)
    # Start authorization request
    integrator = TwitterIntegrator()
    redirect_uri = integrator.get_full_registration_end_url()
    authorization_uri = integrator.create_authorization_url(redirect_uri)
    # Set request token key and secret
    psv_set(
        request, 
        'twitter_oauth_request_token_key', 
        integrator.get_request_token_key()
    )
    psv_set(
        request, 
        'twitter_oauth_request_token_secret', 
        integrator.get_request_token_secret()
    )
    return HttpResponseRedirect(authorization_uri)

@never_cache
def twitter_authorization_redirection_end(request):
    integrator = TwitterIntegrator()
    if 'oauth_token' in request.GET and \
        'oauth_verifier' in request.GET:
        oauth_token = request.GET.get('oauth_token')
        oauth_verifier = request.GET.get('oauth_verifier')
        
        redirect_uri = integrator.get_full_registration_end_url()
        request_token_key = psv_get(
            request,
            'twitter_oauth_request_token_key',
            None
        )
        request_token_secret = psv_get(
            request,
            'twitter_oauth_request_token_secret',
            None
        )

        access_token_dict = integrator.get_access_token_dict(
            redirect_uri, 
            request_token_key,
            request_token_secret,
            oauth_verifier
        )

    else:
        access_token_dict = None 
    if access_token_dict is not None:
        psv_set(
            request, 
            'twitter_access_token_key', 
            access_token_dict['key']
        )
        psv_set(
            request, 
            'twitter_access_token_secret', 
            access_token_dict['secret'])
        integrator.add_twitter_user_record(
            access_token_dict['key'],
            access_token_dict['secret'],
            request.user
        )
        return redirect('show_user_profile', request.user.id)
        
    # TODO: fix this, in case url returns without an oauth code, which
    # shouldn't happen anyway.
    return HttpResponseRedirect(integrator.get_registration_form_url())

@never_cache
def twitter_login_authorization(request):
    # Register expected optional parameters
    params = ('client_id', 'redirect_uri', )
    for p in params:
        v = request.GET.get(p, None)
        if v is not None:
            psv_set(request, 'login_' + p, v)
    # Start authorization request
    integrator = TwitterIntegrator()
    redirect_uri = integrator.get_full_login_end_url()
    authorization_uri = integrator.create_login_url(redirect_uri)
    return HttpResponseRedirect(authorization_uri)

@never_cache
def twitter_login_redirection_end(request):
    integrator = TwitterIntegrator()
    if 'oauth_token' in request.GET and \
       'oauth_verifier' in request.GET:
        oauth_token = request.GET.get('oauth_token')
        oauth_verifier = request.GET.get('oauth_verifier')
        redirect_uri = integrator.get_full_login_end_url()
        request_token_key = psv_get(
            request,
            'twitter_oauth_request_token_key',
            None
        )
        request_token_secret = psv_get(
            request,
            'twitter_oauth_request_token_secret',
            None
        )
        access_token_dict = integrator.get_access_token_dict(
            redirect_uri, 
            request_token_key,
            request_token_secret,
            oauth_verifier
        )
    else:
        access_token_dict = None
    if access_token_dict is not None:
        psv_set(
            request, 
            'twitter_access_token_key', 
            access_token_dict['key']
        )
        psv_set(
            request, 
            'twitter_access_token_secret', 
            access_token_dict['secret']
        )
        # If a Django user associated with the current Twitter account
        # already exists and in that case simply start an authenticathed 
        # session and redirect to proper place depending on the presence 
        # or absence of some session values.
        user = integrator.get_user_by_twitter_user_id(
            access_token_dict['key'],
            access_token_dict['secret']
        )
        if user:
            user.backend = settings.DEFAULT_AUTH_BACKEND
            login(request, user)    
            redirect_uri = get_redirect_uri(request)
            return HttpResponseRedirect(redirect_uri)
        else:
            #FIXME: Refactor this code to show this message without
            # using an extra view since only in this case that page
            # should be reached by the user.
            redirect_uri = reverse('twitter_login_register')
            return HttpResponseRedirect(redirect_uri)
    # Redirect to the default login URL if the process fails
    return HttpResponseRedirect(settings.LOGIN_URL)

#FIXME: Maybe this view will no longer be needed
def twitter_login_register(request):
    return render(request,'login_registration.html')
