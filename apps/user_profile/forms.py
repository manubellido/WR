# -*- coding: utf-8 -*-

from django import forms
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.hashers import UNUSABLE_PASSWORD
from django.contrib.sites.models import get_current_site
from django.template import loader
from django.utils.http import int_to_base36
from django.utils.translation import ugettext_lazy as _

from user_profile.models import UserProfile
from user_profile import strings
from user_profile.constants import EMBEDDING_STYLE_CHOICES
from common.utils.strings import multiple_whitespace_to_single_space


class UserProfileEditForm(forms.ModelForm):

    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = UserProfile
        fields = ('picture', 'hometown', 'id', 'bio')
        widgets = {
                'bio': forms.Textarea(attrs={
                    'rows': '',
                    'cols': ''
                    }),
            }

    def save(self, *args, **kwargs):
        super(UserProfileEditForm, self).save(*args, **kwargs)
        self.instance.user.first_name = self.cleaned_data['first_name']
        self.instance.user.last_name = self.cleaned_data['last_name']
        self.instance.user.save()

# TODO: not used now, should use Django.change_password
class ChangePasswordForm(forms.Form):

    old_password = forms.CharField(
        widget=forms.PasswordInput,
        label=strings.PASSWORD_FORM_OLD_PASSWORD,
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label=strings.PASSWORD_FORM_NEW_PASSWORD,
    )

    new_password_2 = forms.CharField(
        widget=forms.PasswordInput,
        label=strings.PASSWORD_FORM_NEW_PASSWORD_AGAIN,
    )

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean(self):
        oldpass = self.cleaned_data.get('old_pass', None)
        newpass = self.cleaned_data.get('new_pass', None)
        repeated = self.cleaned_data.get('repeat_pass', None)

        if self.user.check_password(oldpass):
            if newpass != repeated:
                raise forms.ValidationError(
                    self.error_messages['invalid_login']
                )
        else:
            raise forms.ValidationError(
                    self.error_messages['invalid_login']
            )


class AccountSettingsForm(forms.ModelForm):

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'type': 'email'}),
    )

    class Meta:
        model = UserProfile
        fields = tuple()
        #fields = ('email',)

        def save(self, *args, **kwargs):
            super(AccountSettingsForm, self).save(*args, **kwargs)
            self.instance.user.email = self.cleaned_data['email']
            self.instance.user.username = self.cleaned_data['email']
            self.instance.user.save()


class LoginForm(forms.Form):

    email = forms.EmailField(
        widget=forms.TextInput(attrs={'type': 'email', 'maxlength': 75}),
        label=_("E-mail")
    )

    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label=_("Password")
    )

    error_messages = {
        'invalid_login': _("Please enter a correct email and password. "
                           "Note that both fields are case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
        'invalid_email': _("Email address invalid"), 
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                us = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages['invalid_email']
                )

            self.user_cache = authenticate(username=us.username,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'])
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(self.error_messages['no_cookies'])

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

class EmbedForm(forms.Form):
    style = forms.ChoiceField(
        choices=EMBEDDING_STYLE_CHOICES
    )

class PasswordResetForm(forms.Form):
    error_messages = {
        'unknown': _("That e-mail address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'unusable': _("The user account associated with this e-mail "
                      "address cannot reset the password."),
    }
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(email__iexact=email,
                                               is_active=True)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password == UNUSABLE_PASSWORD)
               for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            subject = loader.render_to_string(subject_template_name, c)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())

            text_content = loader.render_to_string(email_template_name, c)
            # Missing text content
            html_content = loader.render_to_string(email_template_name, c)

            msg = EmailMultiAlternatives(subject,
                                         text_content,
                                         from_email,
                                         [user.email]
                                         )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
#            send_mail(subject, email, from_email, [user.email])
