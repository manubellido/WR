from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from registration import signals
from registration.models import RegistrationProfile

from user_profile.models import UserProfile
from user_profile.registration.forms import (
    RegisterForm,
    RegisterInvitationForm,
    OrgRegisterForm
)
from organizations.models import Organization

class CustomBackend(object):

    def register(self, request, **kwargs):
        import hashlib
        from numconv import NumConv

        first_name, last_name = kwargs['first_name'], kwargs['last_name']
        email = kwargs['email']
        password = kwargs['password1']

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        # create a hash from email in order to be user as username
        usname = str(hashlib.sha1(email).hexdigest())
        usname = NumConv(16).str2int(usname)
        usname = NumConv(64).int2str(usname)
        # create a new User
        new_user = RegistrationProfile.objects.create_inactive_user(
            usname,
            email,
            password,
            site,
            send_email=not settings.CLOSED_BETA_ACTIVE
         )

        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()

        if settings.CLOSED_BETA_ACTIVE:
            new_user.is_active = True
            new_user.save()

        new_profile = UserProfile(user=new_user)
        new_profile.save()

        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=request
        )

        return new_user

    def register_company(self, request, **kwargs):
        corporate_name = kwargs['corporate_name']
        short_name = kwargs['short_name']
        website = kwargs.get('website', None)
        company_phone = kwargs.get('company_phone', None)
        company_email = kwargs['company_email']
        password = kwargs['password1']
        
        contact_person = kwargs['contact_person']
        contact_person_phone = kwargs.get('contact_person_phone', None)
        contact_person_email = kwargs['contact_person_email']
        contact_person_position = kwargs.get('contact_person_position', None)

        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        new_user = RegistrationProfile.objects.create_inactive_user(
            company_email,
            company_email,
            password,
            site,
            send_email=False
         )

        new_user.first_name = short_name
        new_user.save()

        new_profile = UserProfile(user=new_user, is_organization=True)

        new_organization = Organization(
            user=new_user,
            corporate_name=corporate_name,
            short_name=short_name,
            website=website,
            company_phone=company_phone,
            company_email=company_email,
            contact_person=contact_person,
            contact_person_phone=contact_person_phone,
            contact_person_email=contact_person_email,
            contact_person_position=contact_person_position,
            approved=False
        )
        new_organization.save()
        new_profile.organization = new_organization
        new_profile.save()

        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=request
        )

        return new_user

    # This should return a activated user
    def activate(self, request, activation_key):
        try:
            activated = RegistrationProfile.objects.activate_user(activation_key)
        except RegistrationProfile.DoesNotExist:
            activated = False
            
        if activated:
            signals.user_activated.send(
                sender=self.__class__,
                user=activated,
                request=request
            )
            
        return activated

    def registration_allowed(self, request):
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        return RegisterForm

    def get_organization_form_class(self):
        return OrgRegisterForm

    def get_invitation_form_class(self,request):
        return RegisterInvitationForm

    def post_registration_redirect(self, request, user):
        return ('registration_complete', (), {})

    def post_activation_redirect(self, request, user):
        return ('mycircuits', (), {})
