# -*- coding: utf-8 -*-

try:
    import simplejson as json
except ImportError:
    import json

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import password_change, password_reset
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from user_profile.models import (UserProfile, UserFacebook, UserTwitter,
        UserFollower)
from user_profile.forms import (UserProfileEditForm, AccountSettingsForm,
                                ChangePasswordForm, EmbedForm,
                                PasswordResetForm)
from user_profile.constants import EMBEDDING_FAIL_VALUES
from circuits.forms import make_categories_form
from circuits.models import (Circuit, CircuitRelatedUserProxy,
        CircuitCategoryFollow)
from circuits import settings as circuit_settings
from facebook.integration import FacebookIntegrator
from twitter.integration import TwitterIntegrator


def profile_landing_page(request, user_id):
    return redirect('user_profile.views.user_circuit_list', user_id)


def show_change_success(request):
    return redirect('user_profile.views.show_profile', request.user.id)


def custom_password_reset(request, is_admin_site=False,
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        password_reset_form=PasswordResetForm,
        token_generator=default_token_generator,
        post_reset_redirect=None,
        from_email=None,
        current_app=None,
        extra_context=None):
    if extra_context is None:
        extra_context = {}
    extra_context['STATIC_PREFIX'] = settings.STATIC_PREFIX
    return password_reset(request, is_admin_site, template_name, email_template_name,
            subject_template_name,password_reset_form,token_generator,post_reset_redirect,
            from_email,current_app,extra_context)

def recover_password(request, template_name="registration/password_change_form.html",
                     post_change_redirect = None,
                     password_change_form = PasswordChangeForm,
                     current_app=None, 
                     extra_context = None):
    if extra_context is None:
        extra_context = {}
    extra_context['wr_user'] = request.user
    extra_context['own_profile'] = True
    return password_change(
        request,
        template_name,
        post_change_redirect,
        password_change_form,
        current_app,
        extra_context)

@login_required
def edit_profile(request):
    """
    Place holder for editing user Profile
    Here the user edits his bio, etc that is displayed in show_profile
    """

    if request.method == 'POST':
        form = UserProfileEditForm(
                data=request.POST,
                files=request.FILES,
                instance=request.user.userprofile,
            )
        if form.is_valid():
            form.save()

            return redirect('user_profile.views.show_profile', request.user.id)
            """
            return render(
                    request,
                    'profile/edit_profile.html',
                    {
                        'form': form,
                        'own_profile': True,
                    },
                )
            """
    # default data to be displayed when form is showed
    default_data = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'hometown': request.user.userprofile.hometown,
        'bio': request.user.userprofile.bio,
        'gender': request.user.userprofile.gender,
    }
    form = UserProfileEditForm(default_data, instance=request.user.userprofile)
    template_context = {
        'form': form,
        'wr_user': request.user,
        'own_profile': True,
        }

    try:
        template_context['fb_data'] = UserFacebook.objects.get(user=request.user)
    except UserFacebook.DoesNotExist:
        pass

    try:
        template_context['twitter_data'] = UserTwitter.objects.get(
                user=request.user)
    except UserTwitter.DoesNotExist:
        pass

    return render(
            request,
            'profile/edit_profile.html',
            template_context,
        )


@login_required
def account_settings(request):
    """
    Here the user edits his password, notification and stuff
    """
    # default data to be displayed when form is showed
    default_data = {
        'email': request.user.email,
    }
    account_settings_form = AccountSettingsForm(default_data)

    password_form = ChangePasswordForm(request)

    return render(request,
        'profile/account_settings.html',
        {
            'account_settings_form': account_settings_form,
            'password_form': password_form,
            'wr_user': request.user,
            'own_profile': True,
        },
    )


def show_profile(request, user_id):
    """
    user_id: id of user to show the profile

    wr_user: User showing the display from
    """

    #wr_user = UserProfile.objects.get(user=user_id)
    try:
        wr_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse('No Such User')

    try:
        userprofile = wr_user.userprofile
    except UserProfile.DoesNotExist:
        userprofile = UserProfile(user=wr_user)
        userprofile.save()

    followers = userprofile.get_followers()
    following = userprofile.get_followed_users()
    fav_circuits = userprofile.favorites.all()
    favs = [x.id for x in fav_circuits]

    if request.user.is_authenticated():
        if user_id == str(request.user.id):
            own_profile = True
            following_wr_user = False
        else:
            own_profile = False
            if request.user in followers:
                following_wr_user = True
            else:
                following_wr_user = False
    else:
        following_wr_user = False
        own_profile = False

    user_categories = wr_user.categories.all()
    user_categories_ids = [str(uc.category) for uc in user_categories]
    circuits = Circuit.objects.filter(author=user_id).all()
    categories_form = make_categories_form()

    template_context = {
        'wr_user': wr_user,
        'followers': followers,
        'following': following,
        'following_wr_user': following_wr_user,
        'own_profile': own_profile,
        'sidebar_item': 'profile',
        'circuits': circuits,
        'favs_circuits': fav_circuits,
        'user_categories': user_categories,
        'user_categories_ids': user_categories_ids,
        'favs': favs,
        'categories_form': categories_form,
    }

    wr_user_fb = None
    try:
        wr_user_fb = UserFacebook.objects.get(user=wr_user)
    except UserFacebook.DoesNotExist:
        pass
    if wr_user_fb:
        integrator = FacebookIntegrator()
        fb_data = {
            'fb_name': wr_user_fb.name,
            'fb_link': wr_user_fb.link,
            'fb_picture': \
                integrator.get_profile_picture_url(wr_user_fb.facebook_graphid)
        }
        template_context['fb_data'] = fb_data

    wr_user_twitter = None
    try:
        wr_user_twitter = UserTwitter.objects.get(user=wr_user)
    except UserTwitter.DoesNotExist:
        pass
    if wr_user_twitter:
        integrator = TwitterIntegrator()
        twitter_data = {
            'twitter_name': wr_user_twitter.name,
            'twitter_screen_name': wr_user_twitter.screen_name,
            'twitter_link': wr_user_twitter.link,
            'twitter_picture': integrator.get_user_picture(
                wr_user_twitter.oauth_token_key,
                wr_user_twitter.oauth_token_secret,
                # Can set twitter picture size here
                'bigger'
            )
        }
        template_context['twitter_data'] = twitter_data


    return render(request,
                "profile/show_profile.html",
                template_context,
            )


def show_followers(request, user_id):
    try:
        wr_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse('No Such User')

    user_profile = wr_user.userprofile
    followers = user_profile.get_followers()
    followers_profiles = [UserProfile.objects.get(user=f) for f in followers]
    followers_checked = []
    for follower in followers_profiles:
        struct = {
            'follower': follower,
            'is_following': user_profile.is_following(follower.user)
            }
        followers_checked.append(struct)

    if request.user.is_authenticated():
        if user_id == str(request.user.id):
            own_profile = True
        else:
            own_profile = False

    return render(request,
                "profile/followers.html",
                {
                    'wr_user': wr_user,
                    'followers_checked': followers_checked,
                    'own_profile': own_profile,
                    'sidebar_item': 'followers',
                },
            )


def show_following(request, user_id):
    try:
        wr_user = User.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        return HttpResponse('No Such User')

    user_profile = wr_user.userprofile

    followed_users = user_profile.get_followed_users()
    followed_users_profiles = [
            UserProfile.objects.get(user=f) for f in followed_users
        ]
    followed_users_checked = []
    for followed_user in followed_users_profiles:
        struct = {
            'followed_user': followed_user,
            'is_following': user_profile.is_following(followed_user.user)
            }
        followed_users_checked.append(struct)

    if request.user.is_authenticated():
        if user_id == str(request.user.id):
            own_profile = True
        else:
            own_profile = False

    return render(request,
                "profile/following.html",
                {
                    'wr_user': wr_user,
                    'followed_users_checked': followed_users_checked,
                    'own_profile': own_profile,
                    'sidebar_item': 'following',
                },
            )


#FIXME, just temporal
def follow_user(request, user_id):
    """
    Follow user is an AJAX method
    """
    try:
        user_to_follow = User.objects.get(id=user_id)
    except:
        return HttpResponse('No Such User')
    new_follow = UserFollower(
        owner=user_to_follow,
        follower=request.user
    )
    try:
        new_follow.save()
    except:
        return HttpResponse('Failed')
    return HttpResponse('Success')


@login_required
def favorite_routes_view(request):
    """
    Show a list of favorites circuits for request.user
    """

    circuits_per_page = circuit_settings.DEFAULT_CIRCUITS_LIMIT

    if request.is_ajax():
        page = request.POST.get('page', None)
        if page is not None:
            page = int(page)
        else:
            return HttpResponse(
                json.dumps({'error': 'Missing POST parameter: page'}),
                mimetype='application/json')

        response = {
            'page': int(page) + 1
            }

        circuits = request.user.userprofile.favorites.all(
            )[circuits_per_page * page: circuits_per_age * (page + 1)]
        favs = [ x.id for x in circuits ]

        if circuits:
            html_response = u''

            for circuit in circuits:
                html_response += render_to_string(
                    'circuit/circuit_list_item.html',
                    {'circuit': circuit, 'user': request.user, 'favs': favs})
            response['raw_html'] = html_response

        else:
            response['hide_button'] = True

        return HttpResponse(json.dumps(response),
                            mimetype='application/json')


    # get user_profile from user and get his favorite circuits
    try:
        circuits = request.user.userprofile.favorites.all()[:circuits_per_page]
    except AttributeError:
        circuits = []

    favs = [x.id for x in circuits]

    return render(request,
                'circuits/favorites.html',
                {
                    'circuits': circuits,
                    'favs': favs,
                    'topbar_item': 'favorite_routes',
                },
            )

#@login_required
def user_favorite_routes(request, user_id):
    """
    user_id: id of user to show the profile

    wr_user: Ushow shoing the display of
    """

    circuits_per_page = circuit_settings.DEFAULT_CIRCUITS_LIMIT

    try:
        wr_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse('No Such User')

    try:
        userprofile = wr_user.userprofile
    except UserProfile.DoesNotExist:
        userprofile = UserProfile(user=wr_user)
        userprofile.save()


    if request.is_ajax():
        page = request.POST.get('page', None)
        if page is not None:
            page = int(page)
        else:
            return HttpResponse(json.dumps({'error':
                                            'Missing POST parameter: page'}),
                                mimetype='application/json')

        response = {
            'page': int(page) + 1,
            }


        circuits = userprofile.favorites.all(
            )[circuits_per_page * page: circuits_per_page * (page + 1)]

        if circuits:
            favs = [x.id for x in favs_circuits]
            html_response = u''

            for circuit in circuits:
                html_response += render_to_string(
                    'circuits/circuit_list_item.html',
                    {'circuit': circuit, 'user': request.user})

            response['raw_html'] = html_response

        else:
            response['hide_button'] = True

        return HttpResponse(json.dumps(response),
                            mimetype='application/json')


    fav_circuits = userprofile.favorites.all()[:circuits_per_page]
    favs = [x.id for x in fav_circuits]

    if request.user.id == int(user_id):
        own_profile = True
    else:
        own_profile = False

    return render(request,
            'profile/favorites.html',
            {
                'wr_user': wr_user,
                'circuits': fav_circuits,
                'favs': favs,
                'own_profile': own_profile
            },
        )

#@login_required
def user_circuit_list(request, user_id):
    """
    Show a list of circuits whos author is request.user, this view
    assumes that my route is only show when the user is logged in
    and not anonymous
    """

    circuits_per_page = circuit_settings.DEFAULT_CIRCUITS_LIMIT

    try:
        wr_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse('No Such Response')

    try:
        userprofile = wr_user.userprofile
    except UserProfile.DoesNotExist:
        userprofile = UserProfile(user=wr_user)
        userprofile.save()

    if request.is_ajax():
        page = request.POST.get('page', None)
        if page is not None:
            page = int(page)
        else:
            return HttpResponse(
                json.dumps({'error': 'Missing POST parameter: page'}),
                mimetype='application/json')

        response = {
            'page': int(page) + 1
            }

        circuits = Circuit.objects.filter(author=wr_user
            ).order_by('published', '-created'
            )[circuits_per_page * page: circuits_per_page * (page + 1)]

        if circuits:
            html_response = u''

            for circuit in circuits:
                html_response += render_to_string(
                    'circuit/circuit_list_item.html',
                    {'circuit': circuit, 'user': request.user})
            response['raw_html'] = html_response
        else:
            response['hide_button'] = True

        return HttpResponse(json.dumps(response),
                            mimetype='application/json')

    circuits = Circuit.objects.filter(
                author=wr_user
            ).order_by('published', '-created')[:circuits_per_page]

    if request.user.id == int(user_id):
        own_profile = True
    else:
        own_profile = False

    embed_value = request.GET.get('embed', False)
    
    if embed_value not in EMBEDDING_FAIL_VALUES:
        style = request.GET.get('embedstyle', 'cards')
        return render(request,
            'profile/embedded_circuits.html',
             {
                'domain': settings.SITE_PREFIX,
                'style': style,
                'circuits': circuits,
                'wr_user': wr_user,
                'own_profile': own_profile,
                'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
            },
        )


    return render(request,
        'profile/circuits.html',
        {
            'circuits': circuits,
            'wr_user': wr_user,
            'own_profile': own_profile,
            'STATIC_MAPS_ROOT': settings.STATIC_MAPS_ROOT,
            'GOOGLE_API_KEY': settings.GOOGLE_API_KEY,
        },
    )

def user_circuit_list_embed_form(request, user_id):
    form = EmbedForm()

    if request.method == 'POST':
        form = EmbedForm(data=request.POST)
        if form.is_valid():
            embed_html = '<iframe MAY_BE_MISSING_SOMETHING_HERE src="%s%s?embedded=true&style=%s" ></iframe>' %\
            (
                settings.SITE_PREFIX,
                reverse('user_circuit_list', kwargs={'user_id': user_id}),
                'cards' if form.cleaned_data['style'] == '1' else 'list'
            )
            return render(
                request,
                'profile/user_circuit_list_embed_form.html',
                {
                    'user_id': user_id,
                    'embed_html': embed_html,
                    'form': form,
                    'post': True
                }
            )

    return render(
        request,
        'profile/user_circuit_list_embed_form.html',
        {
            'user_id': user_id,
            'form': form,
            'post': False
        }
    )
