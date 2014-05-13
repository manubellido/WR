#! -*- coding: utf-8 -*-

from ordereddict import OrderedDict

from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from rest.http import HttpResponseCreated
from rest.http import HttpResponseConflict
from rest.http import HttpResponseSeeOther

from rest.views import ResourceView
from rest.views import CollectionResourceView
from rest.views import FunctionResourceView
from rest.views import ControllerResourceView

from rest.utils import render_as_json
from rest.utils import json_error_document
from rest.utils import error_list_from_form
from rest.auth import RESTfulBasicOrDjangoAuthenticationMixIn
from rest.auth import AuthorizationResponse

from user_profile.models import UserProfile
from user_profile import strings
from user_profile.api.forms import RegistrationControllerForm


class UserResource(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ResourceView
):

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', 0)
        try:
            profile = UserProfile.objects.get(user__id=user_id)
            json_document = UserResource.json_representation(profile)
            return HttpResponse(
                content=json_document,
                content_type='application/json',
            )

        except User.DoesNotExist:
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_USER)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json',
            )

    @staticmethod
    def json_representation(profile, render_json=True):
        # Gender subdoc
        gender_subdoc = OrderedDict()
        gender_subdoc['value'] = profile.gender
        gender_subdoc['key'] = UserProfile.GENDER_CHOICES.get_key(
            profile.gender
        )
        gender_subdoc['description'] = profile.get_gender_display()
        # Main document
        document = OrderedDict()
        document['id'] = profile.user.pk
        document['uuid'] = profile.uuid
        document['name'] = profile.user.get_full_name()
        document['bio'] = profile.bio
        document['gender'] = gender_subdoc
        document['member_since'] = profile.created
        document['link'] = profile.get_restful_link_metadata(rel='self')
        if render_json:
            return render_as_json(document)
        else:
            return document


class UserMeFunction(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    FunctionResourceView
):

    def run(self, request, *args, **kwargs):
        user_id = request.user.pk
        try:
            profile = UserProfile.objects.get(user__id=user_id)
            json_document = UserResource.json_representation(profile)
            return HttpResponse(
                content=json_document,
                content_type='application/json',
            )

        except User.DoesNotExist:
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_USER)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json',
            )


class IsFollowerFunction(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    FunctionResourceView
):

    def run(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', 0)
        if user_id > 0:
            try:
                followee = User.objects.get(pk=user_id)
                follower_id = request.GET.get('follower_id', 0)
                if follower_id == 0:
                    follower_id = request.user.pk
                # Check if the user is different
                if followee.id != follower_id:
                    try:
                        follower = User.objects.get(pk=follower_id)
                        try:
                            is_follower = followee.userprofile.is_follower(
                                follower
                            )
                        except UserProfile.DoesNotExist:
                            is_follower = None
                            message = strings.NON_EXISTANT_FOLLOWEE_PROFILE

                    except User.DoesNotExist:
                        is_follower = None
                        message = strings.NON_EXISTANT_FOLLOWER

                    # Send conflict status code
                    if is_follower is None:
                        # Follower does not exist
                        error = OrderedDict()
                        error['message'] = unicode(message)
                        errors = [error]
                        content = json_error_document(errors)
                        return HttpResponseConflict(
                            content=content,
                            content_type='application/json',
                        )
                else:
                    is_follower = False
                # Build response
                document = OrderedDict()
                document['is_follower'] = is_follower
                #FIXME: Add a link to the user and to the available ops
                return HttpResponse(
                    content=render_as_json(document),
                    content_type='application/json',
                )
            except User.DoesNotExist:
                pass

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_USER)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json',
        )


class IsFollowingFunction(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    FunctionResourceView
):

    def run(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', 0)
        if user_id > 0:
            try:
                follower = User.objects.get(pk=user_id)
                followee_id = request.GET.get('followee_id', 0)
                if followee_id == 0:
                    followee_id = request.user.pk
                # Check if the user is different
                if follower.id != followee_id:
                    try:
                        followee = User.objects.get(pk=followee_id)
                        try:
                            is_following = follower.userprofile.is_following(
                                followee
                            )
                        except UserProfile.DoesNotExist:
                            is_following = None
                            message = strings.NON_EXISTANT_FOLLOWER_PROFILE

                    except User.DoesNotExist:
                        is_follower = None
                        message = strings.NON_EXISTANT_FOLLOWEE

                    # Send conflict status code
                    if is_following is None:
                        # Follower does not exist
                        error = OrderedDict()
                        error['message'] = unicode(message)
                        errors = [error]
                        content = json_error_document(errors)
                        return HttpResponseConflict(
                            content=content,
                            content_type='application/json',
                        )
                else:
                    is_following = False
                # Build response
                document = OrderedDict()
                document['is_following'] = is_following
                #FIXME: Add a link to the user and to the available ops
                return HttpResponse(
                    content=render_as_json(document),
                    content_type='application/json',
                )
            except User.DoesNotExist:
                pass

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_USER)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json',
        )


class FollowController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', 0)
        if user_id > 0:
            try:
                followee = User.objects.get(pk=user_id)
                follower = request.user

                if followee == follower:
                    message = strings.SELF_FOLLOW_ERROR
                elif followee.userprofile.is_follower(follower):
                    message = strings.ALREADY_FOLLOWING_USER
                else:
                    # Add follower
                    followee.userprofile.add_follower(follower)
                    # Build response
                    document = OrderedDict()
                    document['is_follower'] = True
                    #FIXME: Add a link to the user and to the available ops
                    document['followee_id'] = followee.pk
                    document['follower_id'] = follower.pk
                    return HttpResponse(
                        content=render_as_json(document),
                        content_type='application/json',
                    )

                # Send conflict status code
                error = OrderedDict()
                error['message'] = unicode(message)
                errors = [error]
                content = json_error_document(errors)
                return HttpResponseConflict(
                    content=content,
                    content_type='application/json',
                )

            except User.DoesNotExist:
                pass

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_USER)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json',
        )


class UnfollowController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', 0)
        if user_id > 0:
            try:
                followee = User.objects.get(pk=user_id)
                follower = request.user

                if followee == follower:
                    message = strings.SELF_FOLLOW_ERROR
                elif not followee.userprofile.is_follower(follower):
                    message = strings.ALREADY_NOT_FOLLOWING_USER
                else:
                    # Remove follower
                    followee.userprofile.remove_follower(follower)
                    # Build response
                    document = OrderedDict()
                    document['is_follower'] = False
                    #FIXME: Add a link to the user and to the available ops
                    document['followee_id'] = followee.pk
                    document['follower_id'] = follower.pk
                    return HttpResponse(
                        content=render_as_json(document),
                        content_type='application/json'
                    )

                # Send conflict status code
                error = OrderedDict()
                error['message'] = unicode(message)
                errors = [error]
                content = json_error_document(errors)
                return HttpResponseConflict(
                    content=content,
                    content_type='application/json'
                )

            except User.DoesNotExist:
                pass

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_USER)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(json_error_document(error_list))


class RegistrationEmailLookupFunction(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    FunctionResourceView
):
    """
    Function that returs if email is already a registered user
    """
    def run(self, request, *args, **kwargs):
        #email = kwargs.get('email', None)
        email = request.GET.get('email', None)
        email_is_valid = False
        if email is not None:
            try:
                existant = User.objects.get(email=email)
                # Return user already registered
                document = OrderedDict()
                document['email'] = unicode(email)
                document['registered'] = True
                return HttpResponse(
                    content=render_as_json(document),
                    content_type='application/json'
                )
            # if user does not exist, return valid email
            except User.DoesNotExist:
                email_is_valid = True

        # Return if email is good to go
        if email_is_valid:
            document = OrderedDict()
            document['email'] = unicode(email)
            document['registered'] = False
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # Return if email is not passed
        error = OrderedDict()
        message = unicode(strings.NO_EMAIL)
        error['message'] = message
        error_list = [error]
        return HttpResponseBadRequest(
            json_error_document(error_list)
        )


class RegistrationController(ControllerResourceView):
    """
    Controller for registering a user
    """
    def run(self, request, *args, **kwargs):
        form = RegistrationControllerForm(request.POST)
        # verify validity of name, email, password fields
        if form.is_valid():
            # validate email is not in use
            if form.valid_email():
                new_user = form.process_objects()
                response = HttpResponseCreated()
                response['Location'] = new_user.userprofile.get_restful_url()
                return response
            else:
                # return mail already in use
                error = OrderedDict()
                error['message'] = unicode(strings.EMAIL_ALREADY_USED)
                error_list = [error]
                return HttpResponseConflict(
                    json_error_document(error_list)
                )

        # Form is not valid
        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json',
            )
