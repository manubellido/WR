# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse, NoReverseMatch

from facebook.integration import FacebookIntegrator
from user_profile.utils import psv_get, psv_set, psv_exists

def get_redirect_uri(request):

    # Grab redirection url if available in the session
    redirect_uri = psv_get(request, 'registration_redirect_uri', None)
    if redirect_uri is not None:
        return redirect_uri

    redirect_uri = psv_get(request, 'login_redirect_uri', None)
    if redirect_uri is not None:
        return redirect_uri

    # Grab redirection url from the client app
    client_id = psv_get(request, 'registration_client_id', None)

    if not client_id:
        client_id = psv_get(request, 'login_client_id', None)

    if client_id:
        try:
            client_app = ClientApp.objects.get(key=client_id)
            # Return this property only if it is not empty
            if client_app.redirect_uri:
                return client_app.redirect_uri
        except ClientApp.DoesNotExist:
            pass

    # Grab default dashboard view
    try:
        return reverse('accounts_user_dashboard')
    except NoReverseMatch:
        return None

def account_add_extra_fields(user):
    account = getattr(user, 'account')
    facebook_user = getattr(user, 'facebookuser')
    something_added = False
    if account and facebook_user and facebook_user.oauth_access_token:
        integrator = FacebookIntegrator()
        access_token = facebook_user.oauth_access_token
        data = integrator.get_account_extra_fields(access_token)
        if len(account.bio.strip()) == 0 and 'bio' in data:
            account.bio = data['bio']
            something_added = True
        if len(account.website.strip()) == 0 and 'website' in data:
            account.bio = data['website']
            something_added = True
        #FIXME: Add support for grabbing the avatar here
    if something_added:
        account.save()
    return something_added
