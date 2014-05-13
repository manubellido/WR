# -*- coding: utf-8 -*-

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.template import RequestContext
from django.conf import settings
from common.decorators.auth import login_forbidden
from registration.backends import get_backend
from django.core.urlresolvers import reverse
from closed_beta.models import Invitation
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMessage
from user_profile import strings
from django.template.loader import render_to_string


@login_forbidden
def register(request, backend, success_url=None, form_class=None,
        disallowed_url='registration_disallowed',
        template_name='registration/registration_form.html',
        extra_context=None):

    backend = get_backend(backend)
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)
    if settings.CLOSED_BETA_ACTIVE and \
        request.session.get('invitation_code','') != '':
        form_class = backend.get_invitation_form_class(request)
    else:
        form_class = backend.get_form_class(request)


    invitation_error = None
    invitation_instance = None

    if settings.CLOSED_BETA_ACTIVE:
        success_url = 'registration_activation_complete'
        if request.session.get('invitation_code', '') == '':
            request.session['invitation_code'] = request.GET.get(
                'code', '')
        else:
            if request.GET.get('code', ''):
                request.session['invitation_code'] = request.GET.get(
                    'code', '')
        try:
            invitation_instance = \
                Invitation.objects.get(code=request.session['invitation_code'])
        except Invitation.DoesNotExist:
            pass

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        invitation_flag = True

        if settings.CLOSED_BETA_ACTIVE and \
                request.session.get('invitation_code', '') != '' and \
                form.is_valid():

            invitation_flag = False
            if invitation_instance:
                invitation_flag = True
                invitation_instance.used = True
                invitation_instance.save()
            else:
                invitation_error = 'Invitation does not Exist'

        if form.is_valid() and invitation_flag:
            if settings.CLOSED_BETA_ACTIVE:
                new_user = backend.register(
                    request,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=invitation_instance.email,
                    password1=form.cleaned_data['password1']
                )
                #Login
                user = authenticate(username=invitation_instance.email
                        , password=form.cleaned_data['password1'])
                login(request, user)
                #Sending invitation mail
                template = "mails/welcome.html"
                context = {}
                context['STATIC_PREFIX'] = settings.STATIC_PREFIX
                context['user'] = user
                message = render_to_string(
                   template,
                   context
                   )
                msg = EmailMessage(
                        strings.WELCOME_MESSAGE,
                        message, settings.EMAIL_HOST_USER, [user.email])
                msg.content_subtype = "html"
                msg.send()
                #Generate reverse for profile
#                success_url = reverse('show_user_profile_info',
 #                           kwargs={'user_id':user.id}
  #                          )
                success_url = reverse('mycircuits')
            else:
                new_user = backend.register(request, **form.cleaned_data)

            if request.session.get('invitation_code', None):
                del request.session['invitation_code']
            else:
                pass
            if success_url is None:
                to, args, kwargs = \
                    backend.post_registration_redirect(request, new_user)
                return redirect(to, *args, **kwargs)
            else:
                return redirect(success_url)
    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    template_context = {'form': form}
    if settings.CLOSED_BETA_ACTIVE:
        template_context['invitation_error'] = invitation_error
        template_context['invitation_instance'] = invitation_instance
        template_context['invitation_code'] = request.session['invitation_code']
        template_context['closed_beta'] = settings.CLOSED_BETA_ACTIVE

    return render(request,
                  template_name,
                  template_context,
                  context_instance=context)

@login_forbidden
def register_company(request, backend, success_url=None, form_class=None,
                     disallowed_url='registration_disallowed',
                     template_name='registration/company_registration_form.html',
                     extra_context=None):

    backend = get_backend(backend)
    if not backend.registration_allowed(request):
        return redirect(disallowed_url)

    form_class = backend.get_organization_form_class()

    success_url = 'company_registration_complete'

    if request.method == 'POST':
        form = form_class(data=request.POST)

        if form.is_valid():
            print 'Form is valid'
            new_user = backend.register_company(
                request,
                **form.cleaned_data
            )
        else:
            context = RequestContext(request)
            return render(request,
                          template_name,
                          {'form': form},
                          context_instance=context)

        if success_url is None:
            to, args, kwargs = \
                backend.post_registration_redirect(request, new_user)
            return redirect(to, *args, **kwargs)
        else:
            return redirect(success_url)

    else:
        form = form_class()

    if extra_context is None:
        extra_context = {}

    context = RequestContext(request)

    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render(request,
                  template_name,
                  {'form': form},
                  context_instance=context)

def activate(request, backend,
    template_name='registration/activate.html',
    success_url=None, extra_context=None, **kwargs
):
    backend = get_backend(backend)
    account = backend.activate(request, **kwargs)
    if account is False:
        raise Http404
    account.backend = 'django.contrib.auth.backends.ModelBackend'

    if account:
        login(request, account)
        if success_url is None:
            to, args, kwargs = backend.post_activation_redirect(request, account)
            return redirect(to, *args, **kwargs)
        else:
            return redirect(success_url)

    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value

    return render(request, template_name, kwargs)
