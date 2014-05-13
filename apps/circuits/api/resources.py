# -*- coding: utf-8 -*-

from ordereddict import OrderedDict

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound)
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import Comment
from django.template.loader import render_to_string

from rest.http import (HttpResponseCreated, HttpResponseConflict,
                       HttpResponseSeeOther, HttpResponseNoContent)
from rest.views import (ResourceView, CollectionResourceView,
                        FunctionResourceView, ControllerResourceView)

from rest.utils import (render_as_json, json_error_document,
                        error_list_from_form)
from rest.auth import RESTfulBasicOrDjangoAuthenticationMixIn
from user_profile.models import UserProfile
from user_profile.signals import category_follow, category_unfollow
from places.api.resources import PlaceResource

from notifications.models import NotifiableEvent

from circuits.api.forms import (CircuitCreationControllerForm,
                                CircuitUpdateControllerForm,
                                CircuitPatchControllerForm,
                                CircuitStopCreationControllerForm,
                                CircuitPictureControllerForm,
                                CircuitCollectionFilterForm,
                                CircuitPublicationStatusForm,
                                CircuitStopUpdateControllerForm)
from circuits.api.authorization import (PostCircuitAuthorizationMixIn,
                                        KwargsCircuitAuthorizationMixIn)
from circuits.constants import CIRCUIT_CATEGORY_CHOICES
from circuits.models import (Circuit, CircuitStop, CircuitCategoryFollow,
                             CircuitRelatedUserProxy)
from circuits.signals import (circuit_visited, circuit_favorited,
                              circuit_unfavorited)
from circuits.utils import CircuitCategory
from circuits import strings


class IsFavoriteFunction(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    FunctionResourceView
):
    """
    RESP API, returns True if user has circuit_id as favorite,
    false otherwise
    """
    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        if circuit_id > 0:
            # get user_profile
            userp = request.user.get_profile()
            is_favorite = userp.favorites.filter(
                pk=circuit_id
            )
            if is_favorite.exists():
                result = True
            else:
                result = False

            # Build response
            document = OrderedDict()
            document['is_favorite'] = result
            #FIXME: Add a link to the circuit
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class IsFollowingCategoryFunction(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    FunctionResourceView
):
    """
    RESP API, returns True if user is following a circuit category,
    otherwise returns False.
    """
    def run(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug', None)
        # optional field for consulting any user
        outside_user_id = request.GET.get('user_id', None)

        if category_slug is not None:
            # get category value
            category_slug = category_slug.upper()

            try:
                cat_id = CIRCUIT_CATEGORY_CHOICES.get_value(category_slug)
            except KeyError:
                # if slug not found, return
                error = OrderedDict()
                message = unicode(strings.NON_EXISTANT_CIRCUIT_CATEGORY)
                error['message'] = message
                error_list = [error]
                return HttpResponseNotFound(
                    content=json_error_document(error_list),
                    content_type='application/json'
                )

            if outside_user_id is None:
                user = request.user
            else:
                try:
                    user = User.objects.get(pk=outside_user_id)
                except User.DoesNotExist:
                    error = OrderedDict()
                    message = unicode(strings.NON_EXISTANT_USER)
                    error['message'] = message
                    error_list = [error]
                    return HttpResponseNotFound(
                        content=json_error_document(error_list),
                        content_type='application/json'
                    )

            # if all went good
            userproxy = CircuitRelatedUserProxy.from_user(user)
            is_following = userproxy.is_following_cat(cat_id)

            # Build response
            document = OrderedDict()
            document['is_following'] = is_following
            #FIXME: Add a link to the circuit
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT_CATEGORY)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class UpvoteController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        existant_circuit = Circuit.objects.filter(pk=circuit_id)

        if existant_circuit.exists():
            # get user_profile from DB
            user = request.user
            # filter if circuit is already favorite
            is_upvoted = user.circuit_ratings.filter(
                circuit__pk=circuit_id
            )
            # check if already upvoted
            if is_upvoted.exists() and is_upvoted[0].vote == 1:
                message = unicode(strings.CIRCUIT_ALREADY_UPVOTED)
            else:
                # Add upvote
                ct = existant_circuit[0]
                ct.register_upvote(user)
                # Build response
                document = OrderedDict()
                #FIXME: Add a link to the circuit
                document['set_upvote'] = True

                # Return response
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

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class DownvoteController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        existant_circuit = Circuit.objects.filter(pk=circuit_id)

        if existant_circuit.exists():
            # get user_profile from DB
            user = request.user
            # filter if circuit is already favorite
            is_downvoted = user.circuit_ratings.filter(
                circuit__pk=circuit_id
            )
            # check if already upvoted
            if is_downvoted.exists() and is_downvoted[0].vote == -1:
                message = unicode(strings.CIRCUIT_ALREADY_DOWNVOTED)
            else:
                # Add downvote
                ct = existant_circuit[0]
                ct.register_downvote(user)
                # Build response
                document = OrderedDict()
                #FIXME: Add a link to the circuit
                document['set_downvote'] = True

                # Return response
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

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class VoteController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        existant_circuit = Circuit.objects.filter(pk=circuit_id)

        if existant_circuit.exists():
            # get user_profile from DB
            user = request.user
            # Add vote
            ct = existant_circuit[0]
            document = OrderedDict()
            vote = request.POST.get('vote', '').strip()

            if vote == '1':
                ct.register_upvote(user)
                document['set_upvote'] = True
            elif vote == '-1':
                ct.register_downvote(user)
                document['set_downvote'] = True
            else:
                ct.reset_vote(user)
                document['reset_vote'] = True

            # Return response
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class AddFavoriteController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
    User adds a circuit as favorite
    """

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        existant_circuit = Circuit.objects.filter(pk=circuit_id)

        if existant_circuit.exists():
            # get user_profile from DB
            userp = request.user.get_profile()
            # filter if circuit is already favorite
            is_favorite = userp.favorites.filter(
                pk=circuit_id
            )
            circuit = Circuit.objects.get(pk=circuit_id)

            # check if already favorited
            if is_favorite.exists():
                message = strings.CIRCUIT_ALREADY_FAVORITE
            # check if request.user is not the author of circuit
            #elif circuit.author == request.user:
            #    message = strings.CIRCUIT_AUTHOR_SELF_FAVORITE
            else:
                # Add favorite
                userp.favorites.add(circuit)
                #Send signal to update Redis DB
                circuit_favorited.send(
                    sender=circuit, 
                    user_id=request.user.id
                )
                # Register notifiable event
                NotifiableEvent.register_event_circuit_favorited(
                    owner=request.user,
                    circuit=circuit,
                )
                # Build response
                document = OrderedDict()
                #FIXME: Add a link to the circuit
                document['set_favorite'] = True

                # Return response
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

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class FollowCategoryController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
    Restful controller that makes a user follow a category
    """

    def run(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug', None)

        if category_slug is not None:
            # get category value
            category_slug = category_slug.upper()

            try:
                cat_id = CIRCUIT_CATEGORY_CHOICES.get_value(category_slug)
            except KeyError:
                # if slug not found, return
                error = OrderedDict()
                message = unicode(strings.NON_EXISTANT_CIRCUIT_CATEGORY)
                error['message'] = message
                error_list = [error]
                return HttpResponseNotFound(
                    content=json_error_document(error_list),
                    content_type='application/json'
                )

            user = request.user
            userproxy = CircuitRelatedUserProxy.from_user(user)
            is_following = userproxy.is_following_cat(cat_id)

            # check if already followed
            if is_following:
                message = strings.CATEGORY_ALREADY_FOLLOWED
            else:
                # Create CircuitCategoryFollow object
                follow_record = CircuitCategoryFollow(
                    user=user,
                    category=cat_id
                )
                # Add favorite
                user.categories.add(follow_record)
                # Shoot signal
                category_follow.send(sender=user, category_id=cat_id)
                # Build response
                document = OrderedDict()
                #FIXME: Add a link to the circuit category and user
                document['is_following'] = True
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

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT_CATEGORY)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class SetFollowCategoriesController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
    Restful controller that makes a user follow a set of categories
    """
    def run(self, request, *args, **kwargs):
        categories = request.POST.getlist('category', [])

        if len(categories) > 0:
            # retrieve user
            user = request.user
            # validate categories and trimm not valid
            valid_categories = []
            for cat in categories:
                if CIRCUIT_CATEGORY_CHOICES.has_value(int(cat)):
                    valid_categories.append(cat)

            # delete all previously followed categories
            prev_cats = user.categories.all()
            for followed_cat in prev_cats:
                # Shoot remove favorite signal
                category_unfollow.send(
                    sender=user, 
                    category_id=followed_cat.category
                )
                # remove from Database
                followed_cat.delete()

            for cat in valid_categories:
                # Create CircuitCategoryFollow object
                follow_record = CircuitCategoryFollow(
                    user=user,
                    category=cat
                )
                # Add favorite
                user.categories.add(follow_record)
                # Shoot signal
                category_follow.send(sender=user, category_id=cat)

            # Build response
            document = OrderedDict()
            # resonse document
            document['is_following_set'] = valid_categories
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # In any other case, return bad request
        error = OrderedDict()
        message = unicode(strings.UNKNOWN_CATEGORY_VALUE)
        error['message'] = message
        error_list = [error]
        return HttpResponseBadRequest(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class RemoveFavoriteController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
    Removes a circuit favorited by user
    """
    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        existant_circuit = Circuit.objects.filter(pk=circuit_id)

        if existant_circuit.exists():
            # get user_profile from DB
            # FIXME: if user is Anonynous this line will give error,
            # but anonymous users wont have favorite options
            userp = request.user.get_profile()
            # filter if circuit is already favorite
            is_favorite = userp.favorites.filter(
                pk=circuit_id
            )

            # check if already favorited
            if not is_favorite.exists():
                message = strings.CIRCUIT_NOT_IN_FAVORITE
            else:
                # get the favorited circuit
                fav_circuit = Circuit.objects.get(pk=circuit_id)
                # Remove favorite
                userp.favorites.remove(fav_circuit)
                #Send signal to update Redis DB
                circuit_unfavorited.send(
                    sender=fav_circuit,
                    user_id=request.user.id
                )
                # Build response
                document = OrderedDict()
                document['unset_favorite'] = True
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

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class UnfollowCategoryController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
    REST API for removing categories followed by user
    """

    def run(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug', None)

        if category_slug is not None:
            # get category value
            category_slug = category_slug.upper()
            try:
                cat_id = CIRCUIT_CATEGORY_CHOICES.get_value(category_slug)
            except KeyError:
                # if slug not found, return
                error = OrderedDict()
                message = unicode(strings.NON_EXISTANT_CIRCUIT_CATEGORY)
                error['message'] = message
                error_list = [error]
                return HttpResponseNotFound(
                    content=json_error_document(error_list),
                    content_type='application/json'
                )

            user = request.user
            userproxy = CircuitRelatedUserProxy.from_user(user)
            is_following = userproxy.is_following_cat(cat_id)

            # check if already followed
            if is_following:
                # Get CircuitCategoryFollow from DB
                follow_record = CircuitCategoryFollow.objects.get(
                    user=user,
                    category=cat_id
                )
                # Remove favorite
                follow_record.delete()
                # Shoot signal delete following cat
                category_unfollow.send(
                    sender=user, 
                    category_id=cat_id
                )
                # Build response
                document = OrderedDict()
                #FIXME: Add a link to the circuit
                document['is_following'] = False
                return HttpResponse(
                    content=render_as_json(document),
                    content_type='application/json'
                )
            else:
                message = strings.CATEGORY_NOT_FOLLOWED

            # Send conflict status code
            error = OrderedDict()
            error['message'] = unicode(message)
            errors = [error]
            content = json_error_document(errors)
            return HttpResponseConflict(
                content=content,
                content_type='application/json'
            )

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT_CATEGORY)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class CircuitCollection(CollectionResourceView):
    """
    Returns a Json with a list of selected circuits with different criteria
    """
    def get(self, request, *args, **kwargs):

        form = CircuitCollectionFilterForm(request.GET)
        if form.is_valid():
            document = OrderedDict()
            document['link'] = self.get_restful_link_metadata(rel='self')
            document['circuits'] = []
            # get circuits from Form
            circuits = form.get_circuits()
            # append each circuit metadata to a list
            for ct in circuits:
                document['circuits'].append(ct.get_restful_link_metadata())

            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
             )

        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json'
            )

    def get_restful_url(self):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('circuit_collection_resource')
        )

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = unicode(strings.CIRCUIT_COLLECTION_NAME)
        metadata['type'] = 'application/json'
        return metadata


class CircuitCategoryCollection(CollectionResourceView):
    """
    Returns a Json with a key=categories and a list of
    links to every category metadata
    """
    def get(self, request, *args, **kwargs):
        categories = []
        all_keys = CIRCUIT_CATEGORY_CHOICES.keys()
        for key in all_keys:
            categories.append(
                CircuitCategoryResource.restful_link_metadata(key)
            )
        document = OrderedDict()
        document['categories'] = categories
        document['link'] = self.get_restful_link_metadata(rel='self')
        document['type'] = 'application/json'
        return HttpResponse(
            content=render_as_json(document),
            content_type='application/json',
        )

    def get_restful_url(self):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('circuit_category_collection_resource')
        )

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = unicode(strings.CIRCUIT_CATEGORY_COLLECTION_NAME)
        metadata['type'] = 'application/json'
        return metadata


class CircuitCategoryResource(ResourceView):

    def get(self, request, *args, **kwargs):
        category_slug = kwargs.get('category_slug', 0)
        # check if key is in Enumeration
        if category_slug.upper() in CIRCUIT_CATEGORY_CHOICES.keys():
            json_document = CircuitCategoryResource.json_representation(
                category_slug
            )
            return HttpResponse(
                content=json_document,
                content_type='application/json',
            )
        else:
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_CIRCUIT_CATEGORY)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

    @staticmethod
    def json_representation(key, render_json=True):
        # check if key is in Enumeration
        key = key.upper()
        if key in CIRCUIT_CATEGORY_CHOICES.keys():
            ccat = CircuitCategory(CIRCUIT_CATEGORY_CHOICES.get_value(key))
            return ccat.get_json_representation(render_json)
        else:
            return None

    @staticmethod
    def restful_link_metadata(key):
        # check if key is in Enumeration
        key = key.upper()
        if key in CIRCUIT_CATEGORY_CHOICES.keys():
            ccat = CircuitCategory(CIRCUIT_CATEGORY_CHOICES.get_value(key))
            return ccat.get_restful_link_metadata()
        else:
            return None

    @staticmethod
    def restful_url(key):
        # check if key exists
        if key in CIRCUIT_CATEGORY_CHOICES.keys():
            ccat = CircuitCategory(CIRCUIT_CATEGORY_CHOICES.get_value(key))
            return ccat.get_restful_url()
        else:
            return ''


class CircuitResource(ResourceView):

    def get(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        try:
            circuit = Circuit.objects.get(pk=circuit_id)
            # Send event signal to Redis DB
            circuit_visited.send(sender=circuit, request=request)
            json_document = CircuitResource.json_representation(circuit)
            return HttpResponse(
                content=json_document,
                content_type='application/json'
            )

        except Circuit.DoesNotExist:
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_CIRCUIT)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

    @staticmethod
    def json_representation(circuit, render_json=True):
        document = OrderedDict()
        document['id'] = circuit.pk
        document['uuid'] = circuit.uuid
        # Name
        document['name'] = circuit.name
        # Category
        document['category'] = CircuitCategoryResource.json_representation(
            CIRCUIT_CATEGORY_CHOICES.get_key(circuit.category),
            render_json=False
        )
        # Description
        document['description'] = circuit.description
        # Picture
        picture_subdoc = OrderedDict()
        picture_subdoc['original'] = circuit.get_picture_url()
        picture_thumbnails_subdoc = OrderedDict()
        aux = circuit.get_picture_url(settings.THUMB_SQUARE_SIZE)
        picture_thumbnails_subdoc['squared'] = aux
        picture_subdoc['thumbnails'] = picture_thumbnails_subdoc
        document['picture'] = picture_subdoc
        # Author
        try:
            document['author'] = \
                circuit.author.userprofile.get_restful_link_metadata()
        except UserProfile.DoesNotExist:
            document['author'] = None
        document['rating'] = circuit.rating
        topics = []
        for tp in circuit.topics.all():
            topics.append(tp.get_restful_link_metadata())
        document['topics'] = topics
        ct_stops = []
        for stop in circuit.circuit_stops.all():
            aux = CircuitStopResource.short_json_representation(
                stop, render_json=False
            )
            ct_stops.append(aux)
        document['circuit_stops'] = ct_stops
        document['coordinates_box'] = circuit.get_coordinates_box()
        # Publication status
        document['published'] = circuit.published
        document['adult_content'] = circuit.adult_content
        # Remix status
        if circuit.remixed_from:
            document['remixed_from'] = \
                circuit.remixed_from.get_restful_link_metadata()
        else:
            document['remixed_from'] = None
        if render_json:
            return render_as_json(document)
        else:
            return document


class CircuitStopResource(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ResourceView
):

    def get(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        stop_id = kwargs.get('stop_id', 0)
        try:
            circuit_stop = CircuitStop.objects.get(
                circuit__pk=circuit_id,
                pk=stop_id
            )
            json_document = CircuitStopResource.json_representation(
                circuit_stop
            )
            return HttpResponse(
                content=json_document,
                content_type='application/json',
            )
        except CircuitStop.DoesNotExist:
            error = OrderedDict()
            message = unicode(
                strings.NON_EXISTANT_STOP % {
                    'stop_id': stop_id, 
                    'circuit_id': circuit_id
                    }
            )
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

    @staticmethod
    def json_representation(circuit_stop, render_json=True):
        document = OrderedDict()
        document['id'] = circuit_stop.id
        document['description'] = unicode(circuit_stop.description)
        document['position'] = circuit_stop.position
        # Circuit
        document['circuit'] = circuit_stop.circuit.get_restful_link_metadata()
        # Place
        document['place'] = circuit_stop.place.get_restful_link_metadata()
        # Picture
        picture_subdoc = OrderedDict()
        picture_subdoc['original'] = circuit_stop.get_picture_url()
        picture_thumbnails_subdoc = OrderedDict()
        aux = circuit_stop.get_picture_url(settings.THUMB_SQUARE_SIZE)
        picture_thumbnails_subdoc['squared'] = aux
        picture_subdoc['thumbnails'] = picture_thumbnails_subdoc
        document['picture'] = picture_subdoc
        # Actions
        document['update_url'] = circuit_stop.get_update_url()
        # Self reference
        document['link'] = \
            circuit_stop.get_restful_link_metadata(rel='self')
        if render_json:
            return render_as_json(document)
        else:
            return document

    @staticmethod
    def short_json_representation(circuit_stop, render_json=True):
        document = OrderedDict()
        document['id'] = circuit_stop.id
        document['position'] = circuit_stop.position
        # Place
        document['place'] = PlaceResource.short_json_representation(
            circuit_stop.place, render_json=False
        )
        # Picture
        picture_subdoc = OrderedDict()
        picture_subdoc['original'] = circuit_stop.get_picture_url()
        picture_thumbnails_subdoc = OrderedDict()
        aux = circuit_stop.get_picture_url(settings.THUMB_SQUARE_SIZE)
        picture_thumbnails_subdoc['squared'] = aux
        picture_subdoc['thumbnails'] = picture_thumbnails_subdoc
        document['picture'] = picture_subdoc
        # Actions
        document['update_url'] = circuit_stop.get_update_url()
        # Self reference
        document['link'] = \
            circuit_stop.get_restful_link_metadata(rel='self')
        if render_json:
            return render_as_json(document)
        else:
            return document


class CircuitRemixController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
        API view-like for remixing a circuit, method=POST,
        uses circuits.models methods to clone a circuit and
        redirects to circuit_edit
    """
    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)

        if Circuit.objects.filter(pk=circuit_id).exists:
            original_circuit = Circuit.objects.get(pk=circuit_id)
        else:
            # Return a 404
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_CIRCUIT)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json',
                )

        # Obtain parameters
        new_title = request.POST.get('new_title', None)
        new_category = request.POST.get('new_category', None)
        new_description = request.POST.get('new_description', None)
        new_author = request.user  # Mixin guarantees logged user

        if new_title is None:
            #Not enough parameters
            error = OrderedDict()
            message = unicode("Missing parameter: new_title")
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json',
                )

        if new_category is None:
            new_category = original_circuit.category

        remixed_circuit = original_circuit.remix(
            new_author=new_author,
            new_title=new_title,
            new_category=new_category,
            new_description=new_description,
            )

        # Register notifiable event
        NotifiableEvent.register_event_circuit_remixed(
            owner=request.user,
            remixed_circuit=remixed_circuit,
            original_circuit=original_circuit,
            timestamp=remixed_circuit.created,
            )
        # Build response Created
        response = HttpResponseCreated()
        # FIXME: not sure if the Location is correct
        response['Location'] = remixed_circuit.get_restful_url()
        return response


class CircuitCreationController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        form = CircuitCreationControllerForm(request.POST)
        if form.is_valid():
            objects = form.process_objects(author=request.user)
            # Register notifiable event
            NotifiableEvent.register_event_circuit_created(
                owner=request.user,
                circuit=objects['circuit'],
                timestamp=objects['circuit'].created
            )
            if objects['multiple']:
                document = OrderedDict()
                circuit = objects['circuit']
                metadata = circuit.get_restful_link_metadata()
                document['circuit'] = metadata
                document['new_topics'] = []
                for topic in objects['new_topics']:
                    metadata = topic.get_restful_link_metadata()
                    document['new_topics'].append(metadata)
                content = render_as_json(document)
                return HttpResponse(
                    content=content,
                    content_type='application/json'
                 )
            else:
                response = HttpResponseCreated()
                response['Location'] = objects['circuit'].get_restful_url()
                return response
        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json'
            )

class CircuitPatchController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    PostCircuitAuthorizationMixIn,
    ControllerResourceView
):
    def run(self, request, *args, **kwargs):
        circuit = Circuit.objects.get(pk=kwargs['circuit_id'])
        form = CircuitPatchControllerForm(request.POST,instance=circuit)
        if form.is_valid():
            form.save()
            return HttpResponseNoContent()
        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json'
            )

class CircuitUpdateController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    PostCircuitAuthorizationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        form = CircuitUpdateControllerForm(request.POST)
        if form.is_valid():
            objects = form.process_objects(author=request.user)
            # Register notifiable event
            NotifiableEvent.register_event_circuit_updated(
                owner=request.user,
                circuit=objects['circuit'],
                timestamp=objects['circuit'].modified
            )
            if objects['multiple']:
                document = OrderedDict()
                circuit = objects['circuit']
                metadata = circuit.get_restful_link_metadata()
                document['circuit'] = metadata
                document['new_topics'] = []
                for topic in objects['new_topics']:
                    metadata = topic.get_restful_link_metadata()
                    document['new_topics'].append(metadata)
                content = render_as_json(document)
                return HttpResponse(
                    content=content,
                    content_type='application/json'
                 )
            else:
                response = HttpResponseSeeOther()
                response['Location'] = objects['circuit'].get_restful_url()
                return response
        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json'
            )


class CircuitPictureController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    PostCircuitAuthorizationMixIn,
    ControllerResourceView):

    def run(self, request, *args, **kwargs):
        form = CircuitPictureControllerForm(request.POST, request.FILES)
        if form.is_valid():
            circuit = form.process_objects(
                author=request.user,
                circuit_id=kwargs.get('circuit_id', 0)
            )
            document = OrderedDict()
            metadata = circuit.get_restful_link_metadata()
            document['circuit'] = metadata
            document['picture_url_full'] = circuit.get_picture_url()
            picture = circuit.get_picture(settings.THUMB_SMALL_SIZE)
            document['picture_url'] = picture['url']
            document['picture_ratio_hw'] = picture['ratio_hw']
            content = render_as_json(document)
            return HttpResponse(
                content=content,
                content_type='application/json'
                )
        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json'
            )


class CircuitStopCreationController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    KwargsCircuitAuthorizationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):

        # Lookup the circuit by id
        circuit_id = kwargs.get('circuit_id', 0)
        try:
            circuit = Circuit.objects.get(pk=circuit_id)
        except Circuit.DoesNotExist:
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_CIRCUIT)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

        # Circuit has been found, process submitted data
        form = CircuitStopCreationControllerForm(request.POST, request.FILES)

        if form.is_valid():
            objects = form.process_objects(circuit=circuit)

            if not objects['conflict']:
                content = OrderedDict()
                circuit_stop_subdoc = CircuitStopResource.json_representation(
                    objects['circuit_stop'], render_json=False
                )
                cs_place_subdoc = PlaceResource.json_representation(
                    objects['circuit_stop'].place, render_json=False
                )
                circuit_stop_subdoc['place'] = cs_place_subdoc
                content['circuit_stop'] = circuit_stop_subdoc

                if objects['multiple'] and 'place' in objects:
                    place_subdoc = PlaceResource.json_representation(
                        objects['place'], render_json=False
                    )
                    content['place'] = place_subdoc
                # Add picture url to dict for returning it
                # Render the responde as JSON
                content = render_as_json(content)

                return HttpResponse(
                    content=content,
                    content_type='application/json'
                 )

            else:
                error = OrderedDict()
                error['message'] = unicode(strings.PLACE_ALREADY_INCLUDED)
                errors = [error]
                content = json_error_document(errors)
                return HttpResponseConflict(
                    content=content,
                    content_type='application/json'
                )
        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json'
            )


class CircuitStopUpdateController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    KwargsCircuitAuthorizationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):

        # Lookup the circuit by id
        circuit_id = kwargs.get('circuit_id', 0)
        place_id = kwargs.get('place_id', 0)
        try:
            # FIXME: this query may return more than 1 circuit
            # and in that case is gonna fail, if same place 2 times
            # on the same circuit
            cstop = CircuitStop.objects.get(
                circuit__pk=circuit_id,
                place__pk=place_id
            )
        except CircuitStop.DoesNotExist:
            error = OrderedDict()
            message = strings.NON_EXISTANT_CIRCUIT_STOP % (
                circuit_id, place_id
            )
            error['message'] = unicode(message)
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

        # Circuit has been found, process submitted data
        form = CircuitStopUpdateControllerForm(
            request.POST,
            request.FILES,
            instance=cstop
        )

        if form.is_valid():

            form.save()

            document = OrderedDict()
            document['success'] = True
            document['updated_fields'] = form.get_updated_fields()
            document['circuit_stop'] = cstop.get_data()

            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
             )

        else:
            errors = error_list_from_form(form)
            content = json_error_document(errors)
            return HttpResponseBadRequest(
                content=content,
                content_type='application/json'
            )


class CircuitPublicationStatusFunction(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    FunctionResourceView
):

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        if circuit_id > 0:
            try:
                circuit = Circuit.objects.get(pk=circuit_id)
                document = OrderedDict()
                document['published'] = circuit.published
                document['link'] = circuit.get_restful_link_metadata()
                return HttpResponse(
                    content=render_as_json(document),
                    content_type='application/json'
                )
            except Circuit.DoesNotExist:
                pass
        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class CircuitPublishController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
    REST API for making a circuit public, returns a message if error
    """

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)

        try:
            circuit = Circuit.objects.get(pk=circuit_id)
        except Circuit.DoesNotExist:
            # return a circuit not found
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_CIRCUIT)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

        if circuit.author != request.user:
            message = unicode(strings.UNAUTHORIZED_CIRCUIT_EDIT)
        elif circuit.published == True:
            message = unicode(strings.CIRCUIT_ALREADY_PUBLISHED)
        else:
            # publish circuit
            circuit.published = True
            circuit.save()
            # Build response
            document = OrderedDict()
            document['published'] = True
            document['link'] = circuit.get_restful_link_metadata()
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # Send conflict status code
        error = OrderedDict()
        error['message'] = message
        errors = [error]
        content = json_error_document(errors)
        return HttpResponseConflict(
            content=content,
            content_type='application/json'
        )


class CircuitUnpublishController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    ControllerResourceView
):
    """
    REST API for making a circuit not public or just private
    returns a message if error
    """

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)

        try:
            circuit = Circuit.objects.get(pk=circuit_id)
        except Circuit.DoesNotExist:
            # return a circuit not found
            error = OrderedDict()
            message = unicode(strings.NON_EXISTANT_CIRCUIT)
            error['message'] = message
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )

        if circuit.author != request.user:
            message = unicode(strings.UNAUTHORIZED_CIRCUIT_EDIT)
        elif circuit.published == False:
            message = unicode(strings.CIRCUIT_ALREADY_UNPUBLISHED)
        else:
            # publish circuit
            circuit.published = False
            circuit.save()
            # Build response
            document = OrderedDict()
            document['unpublished'] = True
            document['link'] = circuit.get_restful_link_metadata()
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # Send conflict status code
        error = OrderedDict()
        error['message'] = message
        errors = [error]
        content = json_error_document(errors)
        return HttpResponseConflict(
            content=content,
            content_type='application/json'
        )


class CircuitPublicationStatusController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    KwargsCircuitAuthorizationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        if circuit_id > 0:
            try:
                circuit = Circuit.objects.get(pk=circuit_id)
                form = CircuitPublicationStatusForm(
                    data=request.POST,
                    instance=circuit
                )
                if form.is_valid():
                    form.update_publication_status()
                    document = OrderedDict()
                    document['published'] = circuit.published
                    document['link'] = circuit.get_restful_link_metadata()
                    return HttpResponse(
                        content=render_as_json(document),
                        content_type='application/json'
                    )
                else:
                    errors = error_list_from_form(form)
                    content = json_error_document(errors)
                    return HttpResponseConflict(
                        content=content,
                        content_type='application/json'
                    )

            except Circuit.DoesNotExist:
                pass
        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )

class CircuitPostCommentController(
    RESTfulBasicOrDjangoAuthenticationMixIn,
    KwargsCircuitAuthorizationMixIn,
    ControllerResourceView
):

    def run(self, request, *args, **kwargs):
        circuit_id = kwargs.get('circuit_id', 0)
        comment_user_id = int(request.POST.get('comment_user', None))
        if circuit_id > 0 and comment_user_id == request.user.id:
            try:
                circuit = Circuit.objects.get(pk=circuit_id)
                site = Site.objects.get(pk=settings.SITE_ID)
                new_comment = Comment(
                    content_object=circuit,
                    site=site,
                    user=request.user,
                    comment=request.POST.get('comment', None),
                )
                new_comment.save()

                document = OrderedDict()
                html_response = render_to_string(
                    'circuits/comment_list_item.html',
                    {'comment': new_comment}
                )
                document['raw_html'] = html_response
                return HttpResponse(
                    content=render_as_json(document),
                    content_type='application/json'
                )

            except Circuit.DoesNotExist:
                pass
        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_CIRCUIT)
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )
