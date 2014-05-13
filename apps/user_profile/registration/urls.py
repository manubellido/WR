# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse
from django.conf import settings

from user_profile.registration.views import activate, register, register_company
from user_profile.registration.forms import RegisterForm
from closed_beta.utils import invitation_required

CUSTOM_BACKEND = 'user_profile.registration.backends.CustomBackend'

if settings.CLOSED_BETA_ACTIVE:
    register=invitation_required(register)

urlpatterns = patterns('',
   url(r'^activate/complete/$',
       direct_to_template,
       {'template': 'registration/activation_complete.html'},
       name='registration_activation_complete'),
   url(r'^activate/(?P<activation_key>\w+)/$',
       activate,
       {'backend': CUSTOM_BACKEND},
       name='registration_activate'),
   url(r'^register/$',
       register,
       {'backend': CUSTOM_BACKEND,
        'form_class': RegisterForm},
       name='registration_register'),
   url(r'^social_register/$',
       direct_to_template,
       {'template': 'registration/pre_registration_with_social.html'},
       name='social_register'),
   url(r'^register-company/$',
       register_company,
       {'backend': CUSTOM_BACKEND,
        'form_class': RegisterForm},
       name='registration_register_company'),
   url(r'^register/complete/$',
       direct_to_template,
       {'template': 'registration/registration_complete.html'},
       name='registration_complete'),
   url(r'^register-company/complete/$',
       direct_to_template,
       {'template': 'registration/company_registration_complete.html'},
       name='company_registration_complete'),
   url(r'^register/closed/$',
       direct_to_template,
       {'template': 'registration/registration_closed.html'},
       name='registration_disallowed'),
   (r'', include('registration.auth_urls')),
)
