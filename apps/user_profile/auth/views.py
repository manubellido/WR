# -*- coding: utf-8 -*-

import urlparse
import json

from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.conf import settings
from django.http import HttpResponse,HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site

from django.shortcuts import get_object_or_404

from user_profile.models import UserEmail
from user_profile.constants import LANGUAGE_CHOICES


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name='next',
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    """
    Copied django login view except for the language setting part
    """

    if request.method == "POST":

        form = authentication_form(data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Heavier security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = settings.LOGIN_REDIRECT_URL

            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())

            # Setting language to user preference
            #lang_code = LANGUAGE_CHOICES[request.user.userprofile.language][1]
            #request.session['django_language'] = lang_code

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


def verify_email(request, verification_code):
    """
    Check if verification_code corresponds to email
    """

    user_email = get_object_or_404(UserEmail,verification_code=verification_code)
    user_email.verified = True
    user_email.save()

    if user_email.verify_email(verification_code):
        return render(
            request,
            'registration/email_successfully_verified.html',
            {'email': user_email,
             },
            )

    return render(
        request,
        'registration/email_unsuccessfully_verified.html',
        {},
        )


@require_POST
@login_required
def append_email(request):
    """
    Associate new email to user.
    Verifies that a parameter email is passed, that the parameter passed is a
    valid email and the email does not belong to another user
    """
    email = request.POST.get('email', None)
    if email:

        try:
            validate_email(email)
        except ValidationError:
            response = {'status': 'error',
                        'message': 'Enter a valid email',
                        }
            return HttpResponse(json.dumps(response),
                                mimetype='application/json')

        if UserEmail.objects.filter(email=email).exists():
            response = {'status': 'error',
                        'message': 'Email already taken by another user',
                        }
            return HttpResponse(json.dumps(response),
                                mimetype='application/json',)
        user_email = UserEmail(email=email, user=request.user)
        user_email.save()
        user_email.send_verification_email()
        return HttpResponse(json.dumps(
                {'status': 'OK'}),
                            mimetype='application/json')

    else:
        response = {'status': 'error',
                    'message': 'Parameter Email required',
                    }
        return HttpResponse(json.dumps(response),
                            mimetype='application/json',)


@require_POST
@login_required
def remove_email(request):
    """
    TODO: Evaluate if the guard against deleting the last email is needed.
    The default backend to login via the username is still available.
    """
    user = request.user
    if user.emails.count() >= 2:
        email = request.POST.get('email', None)
        if email:
            try:
                user_email = UserEmail.objects.get(user=user, email=email)
            except UserEmail.DoesNotExist:
                response = {'status': 'error',
                            'message': 'The email %s is not associated with'
                            'your account' % (email,)
                            }
                return HttpResponse(json.dumps(response),
                                    mimetype='apllication/json',)

            user_email.delete()
            response = {'status': 'OK',}
            return HttpResponse(json.dumps(response),
                    mimetype='apllication/json',)
        else:
            response = {'status': 'error',
                        'message': 'Parameter Email required',}
            return HttpResponse(json.dumps(response),
                                mimetype='application/json',)
            
    else:
        response = {'status': 'error',
                    'message': 'Cannot Delete Last Email'}
        return HttpResponse(json.dumps(response),
                            mimetype='application/json',)
