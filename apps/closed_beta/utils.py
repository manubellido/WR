# -*- coding: utf-8 -*-

from django.shortcuts import redirect

from user_profile.models import UserProfile
from closed_beta.views import invitation_form
from closed_beta.models import Invitation

def invitation_required(function):
    """
    Decorator, verifies that a view passes a valid code, redirect to
    the invitation form otherwise
    """
    def wrapped(request, *args, **kwargs):
        # obtain invitation code from GET, set to none otherwise
        invitation_code = request.GET.get('code', None)
        
        if invitation_code is None and \
                not request.session.get('invitation_code', None):
            #  when no invitation code, redirect to invitation form
            return redirect('request_invitation')
            # invitation_form(request, *args, **kwargs)
        else:
            if invitation_code:
                try:
                    invitation = Invitation.objects.get(code=invitation_code)
                except Invitation.DoesNotExist:
                    return redirect('request_invitation')
                #invitation_form(request, *args, **kwargs)
            else:
                try:
                    invitation = Invitation.objects.get(
                        code=request.session['invitation_code'])
                except Invitation.DoesNotExist:
                    return redirect('request_invitation')
                #invitation_form(request, *args, **kwargs)
                
                
            # verify that code was not already approved
            if invitation.approved == False:
                return redirect('request_invitation')
                #invitation_form(request, *args, **kwargs)
                
            # verify that invitation was not used
            elif invitation.used == True:
                return redirect('request_invitation')
                #invitation_form(request, *args, **kwargs)
                
            else:    
                #pass on to decorated function
                return function(request, *args, **kwargs)
  
    return wrapped
    
    
def login_required_or_invitation(function):
    """
    Decorator, verifies that a user is logged in, otherwise he is redirected
    to the invitation view
    """
    
    def wrapped(request, *args, **kwargs):
        # verify that user is authenticated
        if not request.user.is_authenticated():
            return redirect('request_invitation')
            #invitation_form(request, *args, **kwargs)
            
        # pass control to decorated function
        else:
            return function(request, *args, **kwargs)
        
    return wrapped

def generate_codes():
    non_coders = Invitation.objects.filter(code=None)
    for invite in non_coders:
        invite.code = Invitation.generate_invitation_code()
        invite.save()

def reduce_invitations():
    users = UserProfile.objects.all()
    for user in users:
        if user.invitations_left > 5:
            user.invitations_left = 5
            user.save()
