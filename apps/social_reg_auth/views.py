# -*- coding: utf-8 -*-

import simplejson
from ordereddict import OrderedDict
from twython import Twython

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, 
    HttpResponseRedirect, 
    HttpResponseForbidden
)
from django.template import RequestContext
from django.shortcuts import (
    render_to_response, 
    get_object_or_404, 
    Http404
)
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import (login, 
    authenticate, 
    logout as django_logout
)
from django.shortcuts import render 

from social_reg_auth import constants
from social_reg_auth.forms import TwitterUserForm
from social_reg_auth.facebook_utils import *
from social_reg_auth.twitter_utils import get_profile_dict
from user_profile.models import UserProfile, UserTwitter, UserFacebook
from common.utils.verbose_password_generator import pass_generator


def facebook_registration(request):
    callback_url = '%s%s' % (
        # FIXME: just for dev porpuses
        constants.SITE_PREFIX,
        #settings.SITE_PREFIX,
        reverse('facebook_registration_callback'),
    )
    url = facebook_create_authorization_url(callback_url)
    return HttpResponseRedirect(url)


def facebook_registration_callback(request):
    if 'code' in request.GET:
        code = request.GET.get('code')
        redirect_uri = '%s%s' % (
            # FIXME: just for dev porpuses
            constants.SITE_PREFIX,
            #settings.SITE_PREFIX,
            reverse('facebook_registration_callback')
        )
        access_token = facebook_get_access_token(redirect_uri, code)
    else:
        access_token = None

    # if access_token is not None:
    #     psv_set(request, 'facebook_access_token', access_token)

    registration_dict = facebook_get_registration_dict(
        access_token=access_token
    )

    fbdata = facebook_get_user_data(
         access_token=access_token
    )

    first_name = registration_dict.get('first_name', '')
    last_name = registration_dict.get('last_name', '')
    email = registration_dict.get('email', '')
    facebook_id = registration_dict.get('id', None)
    try:
        bio = fbdata.get('bio', '')
        hometown = fbdata['hometown'].get('name', '')
    except:
        bio = ''
        hometown = ''

    if request.user.is_authenticated():
        try:
            fb_profile = request.user.facebook_data
            return HttpResponseRedirect(reverse('edit_profile'))
        except:
            fb_profile = UserFacebook(
                user=request.user,
                name=first_name+' '+last_name,
                oauth_access_token=access_token,
            )
            fb_profile.save()
            # add facebook bio and hometown
            up = request.user.userprofile
            up.bio = bio
            up.hometown = hometown
            up.save()
            return HttpResponseRedirect(reverse('edit_profile'))

    try:
        # Search facebook user from graph id
        fb_user = UserFacebook.objects.get(
            facebook_graphid=facebook_id
        )
        user = fb_user.user
    except:
        user = UserProfile.get_or_create(
            email, 
            first_name, 
            last_name, 
            facebook_id,
        )
        # add facebook bio and hometown
        up = user.userprofile
        up.bio = bio
        up.hometown = hometown
        up.save()
        if user is None:
            # something failed authenticating the account, like
            # mail is already in use
            return HttpResponseRedirect(reverse('home'))

    # Hacky way to set backend to user to login
    user.backend='django.contrib.auth.backends.ModelBackend'
    user.save()
    login(request, user)

    return HttpResponseRedirect(reverse('home'))

@login_required
def facebook_unlink(request):
    """ Unlinks the profile of a user with an existing facebook account
    """
    try:
        request.user.facebook_data.delete()
    except:
        pass

    return HttpResponseRedirect(reverse('edit_profile'))

# TWITTER VIEWS

def begin_auth(request, callback_url=None):
    """The view function that initiates the entire handshake.
        For the most part, this is 100% drag and drop."""
    # Instantiate Twython with the first leg of our trip.
    twitter = Twython(
        twitter_token = settings.TWITTER_CONSUMER_KEY,
        twitter_secret = settings.TWITTER_CONSUMER_SECRET,
        callback_url = request.build_absolute_uri(reverse('twitter_callback'))
    )

    # Request an authorization url to send the user to...
    auth_props = twitter.get_authentication_tokens()

    # Then send them over there, durh.
    request.session['request_token'] = auth_props
    return HttpResponseRedirect(auth_props['auth_url'])


def thanks(request, redirect_url=settings.LOGIN_REDIRECT_URL):
    """
        A user gets redirected here after hitting Twitter and authorizing your
        app to use their data. 
        This is the view that stores the tokens you want
        for querying data. Pay attention to this.
    """
    # Now that we've got the magic tokens back from Twitter, we need to exchange
    # for permanent ones and store them...
    twitter = Twython(
        twitter_token = settings.TWITTER_CONSUMER_KEY,
        twitter_secret = settings.TWITTER_CONSUMER_SECRET,
        oauth_token = request.session['request_token']['oauth_token'],
        oauth_token_secret = request.session['request_token']['oauth_token_secret'],
    )

    # Retrieve the tokens we want...
    authorized_tokens = twitter.get_authorized_tokens()

    # check if trying to attach account
    if request.user.is_authenticated():
        try:
            twitter_profile = request.user.twitter_data
        except:
            new_twitter_profile = UserTwitter(
                user = request.user,
                oauth_token_key=authorized_tokens['oauth_token'],
                oauth_token_secret=authorized_tokens['oauth_token_secret'],
                screen_name=authorized_tokens['screen_name'],       
            )
            new_twitter_profile.save()
            # get twitter data
            tw_profile = get_profile_dict(authorized_tokens['screen_name'])
            # get user profile
            up = request.user.userprofile
            up.bio = tw_profile.get('description', '')
            up.hometown = tw_profile.get('location', '')
            up.save()
        
        return HttpResponseRedirect(reverse('edit_profile'))

    # If they already exist, grab them, login and redirect to a page displaying stuff.
    try:
        user_t = UserTwitter.objects.get(
            screen_name=authorized_tokens['screen_name']
        )
        user = user_t.user
        #user = User.objects.get(username = authorized_tokens['screen_name'])
        # Hacky way to set backend to user to login
        user.backend='django.contrib.auth.backends.ModelBackend'
        user.save()
        login(request, user)
        return HttpResponseRedirect(redirect_url)
    except UserTwitter.DoesNotExist:
        # get profile image url and real name
        try:
            profile = get_profile_dict(authorized_tokens['screen_name'])
            fullname = profile['name']
            profile_picture_url = profile['profile_image_url']
        except:
            fullname = None
            profile_picture_url = None

        # set some variables to session
        request.session['twitter_name'] = authorized_tokens['screen_name']
        request.session['oauth_token'] = authorized_tokens['oauth_token']
        request.session['oauth_secret'] = authorized_tokens['oauth_token_secret']
        request.session['twitter_profile_picture'] = profile_picture_url
        request.session['twitter_real_name'] = fullname

        #new_twitter_user(request)
        return HttpResponseRedirect(reverse('twitter_register'))
            
    
def new_twitter_user(request):
    # FORM for user data
    if request.method == 'POST':
        form = TwitterUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            first = form.cleaned_data['first']
            last = form.cleaned_data['last']

            psw = pass_generator()
            user = UserProfile.create_user_with_tokens(
                first=first,
                last=last,
                email=email,
                password=psw,
                twitter_oauth_token=request.session['oauth_token'],
                twitter_oauth_secret=request.session['oauth_secret'],
                facebook_oauth_token=None,
                facebook_graphid=None,
            )

            # Hacky way to set backend to user to login
            user.backend='django.contrib.auth.backends.ModelBackend'
            # Attach user profile picture
            user.userprofile.save_image_from_url(
                request.session['twitter_profile_picture']
            )
            # save model
            user.save()
            # get twitter data
            tw_profile = get_profile_dict(request.session['twitter_name'])
            # get user profile
            up = user.userprofile
            up.bio = tw_profile.get('description', '')
            up.hometown = tw_profile.get('location', '')
            up.save()
            # login new user
            login(request, user)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            context = RequestContext(request)
            return render(
                request,
                'social_reg_auth/twitter_register.html', 
                {
                    'form': form,
                },
                context_instance=context
            )

    # check if real name came from twitter
    if request.session['twitter_real_name'] is not None:
        fullname = request.session['twitter_real_name'].split()
        # split the name into firstname and lastname
        first = fullname[0]
        last = fullname[-1]
        form = TwitterUserForm(initial={
            'first': first, 'last': last
            }
        )
    else: 
        form = TwitterUserForm()

    return render(request, 
        'social_reg_auth/twitter_register.html', 
        {
            'form': form,
            'profile_picture_url': request.session[
                'twitter_profile_picture'
            ],
            'screen_name': request.session['twitter_name'],
        }
    )

@login_required
def twitter_unlink(request):
    """ Unlinks the profile of a user with an existing twitter account
    """
    try:
        request.user.twitter_data.delete()
    except:
        pass

    return HttpResponseRedirect(reverse('edit_profile'))
