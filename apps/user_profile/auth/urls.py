# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.core.urlresolvers import reverse

from user_profile.auth import views
from user_profile.auth.forms import HtmlPasswordResetForm
from user_profile.views import recover_password, custom_password_reset
from user_profile.forms import LoginForm

urlpatterns = patterns('',
    url(r'^login/$',
        'user_profile.auth.views.login',
        {'template_name': 'registration/login.html',
         'authentication_form': LoginForm},
        name='auth_login'),
    url(r'^logout/$',
        'django.contrib.auth.views.logout_then_login',
        {'login_url': '/'},
        name='auth_logout_then_login'),
    url(r'^settings/$',
        recover_password,
        {'post_change_redirect': '/password/change/done/',},
        name='account_settings'),
    url(r'^password/change/done/$',
        'user_profile.views.show_change_success',
        name='auth_password_change_done'),
    url(r'^password/reset/$',
        custom_password_reset,
        {'template_name': 'registration/reset_password.html',
         'email_template_name': 'mails/passwordReset.html',
         'password_reset_form': HtmlPasswordResetForm,},
        name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete',
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'registration/reset_done.html'},
        name='auth_password_reset_done'),
    url(r'^append_email/$',
        views.append_email,
        name='append_email'),
    url(r'^remove_email/$',
        views.remove_email,
        name='remove_email'),
)
