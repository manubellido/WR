# -*- coding: utf-8 -*-

from ordereddict import OrderedDict

from django import forms
from django.contrib.auth.models import User
from user_profile.models import UserProfile

from common.utils.strings import multiple_whitespace_to_single_space

class RegistrationControllerForm(forms.Form):

    first = forms.CharField(
        max_length=128,
        required=False
    )
    
    last = forms.CharField(
        max_length=128,
        required=False
    )

    email = forms.EmailField(
        max_length=128,
        required=True
    )

    password = forms.CharField(
        max_length=128,
        required=True
    )
    
    facebook_oauth_token = forms.CharField(
        max_length=200,
        required=False
    )
    
    facebook_graphid = forms.CharField(
        max_length=20,
        required=False
    )
    
    twitter_oauth_token = forms.CharField(
        max_length=100,
        required=False
    )

    twitter_oauth_secret = forms.CharField(
        max_length=100,
        required=False
    )
   
    def valid_email(self):
        # check if email is already in use
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            return False
        return True

    def process_objects(self): 
        # Create user passing fields
        user = UserProfile.create_user_with_tokens(
            first=self.cleaned_data['first'],
            last=self.cleaned_data['last'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            facebook_oauth_token=self.cleaned_data.get(
                'facebook_oauth_token', None
            ),
            facebook_graphid=self.cleaned_data.get('facebook_id', None),
            twitter_oauth_token=self.cleaned_data.get(
                'twitter_oauth_token', None
            ),
            twitter_oauth_secret=self.cleaned_data.get(
                'twitter_oauth_secret', None
            )
        )
        return user
        


