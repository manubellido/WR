# -*- coding: utf-8 -*-

from facepy import GraphAPI
from django.contrib.auth.models import User

from user_profile.models import UserCredentials
from suggestions.models import (FBInviteSuggestion, TwitterInviteSuggestion,
                                Follow_Suggestion)


def get_fb_friends(user):
    fb_api = GraphAPI(user.credentials.facebook_access_token)
    friends = fb_api.get('me/friends')['data']

    for fb_user in friends:
        fb_user['profile_picture'] = 'https://graph.facebook.com/%s/picture' %\
            fb_user['id']
        try:
            found_user = UserCredentials.objects.get(
                facebook_graphid=fb_user['id'])
            fb_user['in_worldrat'] = True
            fb_user['worldrat_user'] = found_user.user
        except UserCredentials.DoesNotExist:
            fb_user['in_worldrat'] = False

    return friends

def make_suggestions(user):
    fb_friends = get_fb_friends(user)
    
    for fb_user in fb_friends:
        if fb_user['in_worldrat']:
            follow_suggestion = FollowSuggestion(
                source='Facebook',
                receiving_user=user,
                suggested_user=fb_user['worldrat_user']
            )
            follow_suggestion.save()            
        else:
            invite_suggestion = FBInviteSuggestion(
                suggesting_to=user,
                suggested_fb_id=fb_user['id'],
            )
            invite_suggestion.save()

def get_pending_invites(user):
    pending = FBInviteSuggestion.objects.filter(suggesting_to=user).all()
    print pending
    return pending

def get_pending_follows(user):
    pending = FollowSuggestion.objects.filter(receiving_user=user).all()
    print pending
    return pending
