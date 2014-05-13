#! -*- coding: utf-8 -*-

import django.utils.simplejson as json

from ordereddict import OrderedDict
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.conf import settings
from rest.views import ResourceView
from rest.views import ControllerResourceView
from rest.views import CollectionResourceView
from rest.views import FunctionResourceView
from rest.http import HttpResponseConflict
from rest.auth import RESTfulBasicOrDjangoAuthenticationMixIn as AuthMixIn
from rest.utils import render_as_json
from rest.utils import json_error_document
from rest.utils import error_list_from_form
from places.models import Place, PlaceType, DonePlace
from places import strings


class IsDonePlaceFunction(
    AuthMixIn,
    FunctionResourceView
):
    """
    RESP API, returns True if user has place_is as DonePlace,
    false otherwise
    """
    def run(self, request, *args, **kwargs):
        place_id = kwargs.get('place_id', 0)
        if place_id > 0:
            user = request.user
            try:
                is_done = user.done_place_records.filter(
                    place__pk=place_id
                )
                if is_done.exists():
                    result = True
                else:
                    result = False
            except DonePlace.DoesNotExist:
                result = False

            # Build response
            document = OrderedDict()
            document['is_done'] = result
            return HttpResponse(
                content=render_as_json(document),
                content_type='application/json'
            )

        # In any other case, return a 404
        error = OrderedDict()
        message = unicode(strings.NON_EXISTANT_PLACE % {
            'place_id': place_id,
            })
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class AddDonePlaceController(
    AuthMixIn,
    ControllerResourceView
):
    """
    REST API for adding a place as Done
    """
    def run(self, request, *args, **kwargs):
        place_id = kwargs.get('place_id', 0)
        existant_place = Place.objects.filter(pk=place_id)

        if existant_place.exists():
            # get user
            user = request.user
            # filter if place is already marked as DonePlace
            is_done = user.done_place_records.filter(
                place__pk=place_id
            )
            # check if already favorited
            if is_done.exists():
                message = strings.PLACE_ALREADY_DONE
            else:
                # Add DonePlace
                dp = DonePlace(user=user, place=existant_place[0])
                dp.save()

                # Build response
                document = OrderedDict()
                #FIXME: Add a link to the Place
                document['set_doneplace'] = True

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
        message = unicode(strings.NON_EXISTANT_PLACE % {
            'place_id': place_id
            })
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class RemoveDonePlaceController(
    AuthMixIn,
    ControllerResourceView
):
    """
    REST API for removing a place a DonePlace
    """
    def run(self, request, *args, **kwargs):
        place_id = kwargs.get('place_id', 0)
        existant_place = Place.objects.filter(pk=place_id)

        if existant_place.exists():
            # get user
            user = request.user
            # filter if circuit is already favorite
            is_done = user.done_place_records.filter(
                place__pk=place_id
            )
            # check if is not marked as Done
            if not is_done.exists():
                message = strings.PLACE_NOT_DONE
            else:
                # get DonePlace instance object
                dp = is_done[0]
                # delete DonePlace
                dp.delete()
                # Build response
                document = OrderedDict()
                document['unset_doneplace'] = True
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
        message = unicode(strings.NON_EXISTANT_PLACE % {
            'place_id': place_id
            })
        error['message'] = message
        error_list = [error]
        return HttpResponseNotFound(
            content=json_error_document(error_list),
            content_type='application/json'
        )


class PlaceResource(AuthMixIn, ResourceView):

    def get(self, request, *args, **kwargs):
        place_id = kwargs.get('place_id', 0)
        try:
            place = Place.objects.get(place_id=place_id)
            json_document = PlaceResource.json_representation(place)
            return HttpResponse(json_document)
        except Place.DoesNotExist:
            error = OrderedDict()
            message = strings.NON_EXISTANT_PLACE % {'place_id': place_id}
            error['message'] = unicode(message)
            error_list = [error]
            return HttpResponseNotFound(json_error_document(error_list))
    
    @staticmethod
    def json_representation(place, render_json=True):
        # Document
        document = OrderedDict()
        document['name'] = place.name
        document['place_type'] = \
            place.get_place_type().get_json_representation(False)
        document['coordinates'] = place.get_coordinates_subdoc()
        document['address'] = place.address
        document['city'] = place.get_city_name()
        document['state'] = place.get_state_name()
        document['country'] = place.get_country_name()
        document['phone_number'] = place.phone_number
        document['website'] = place.website
        document['link'] = place.get_restful_link_metadata(rel='self')
        if render_json:
            return render_as_json(document)
        else:
            return document

    @staticmethod
    def short_json_representation(place, render_json=True):
        document = OrderedDict()
        document['name'] = place.name
        document['coordinates'] = place.get_coordinates_subdoc()
        document['address'] = place.address
        document['link'] = place.get_restful_link_metadata(rel='self')
        if render_json:
            return render_as_json(document)
        else:
            return document
            
             
class PlaceCategoryResource(ResourceView):
    """
    Returns the representation of a venue/categorie, place_type as in DB
    """

    def get(self, request, *args, **kwargs):
        placetype_id = kwargs.get('place_type_id', 0)
        try:
            placetype = PlaceType.objects.get(place_type_id=placetype_id)
            json_document = PlaceCategoryResource.json_representation(
                placetype
            )
            return HttpResponse(
                content=json_document,
                content_type='application/json'
            )
        except PlaceType.DoesNotExist:
            error = OrderedDict()
            message = strings.UNKNOWN_PLACE_TYPE % {'placetype_id': placetype_id}
            error['message'] = unicode(message)
            error_list = [error]
            return HttpResponseNotFound(
                content=json_error_document(error_list),
                content_type='application/json'
            )
    
    @staticmethod
    def json_representation(placetype, render_json=True):
        # Document
        document = OrderedDict()
        document['name'] = placetype.name
        document['pluralName'] = placetype.pluralName
        document['shortName'] = placetype.shortName
        document['icon_prefix'] = placetype.icon_prefix
        document['icon_sizes'] = placetype.icon_sizes
        document['icon_name'] = placetype.icon_name
        document['link'] = placetype.get_restful_link_metadata(rel='self')
        if render_json:
            return render_as_json(document)
        else:
            return document            


class PlaceCategoryCollection(CollectionResourceView):
    """
    Returns a Json with a key=categories and a list of
    links to every category metadata
    """
    def get(self, request, *args, **kwargs):
        document = OrderedDict()
        # returns the same JSON FS gives
        document['place_types'] = json.loads(
            PlaceCategoryCollection.json_representation()
        )
        document['link'] = self.get_restful_link_metadata(rel='self')
        return HttpResponse(
            content=render_as_json(document),
            content_type='application/json'
        )

    def get_restful_url(self):
        return "%s%s" % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('place_categories_resource')
        )

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = unicode(strings.PLACE_TYPE_COLLECTION)
        metadata['type'] = 'application/json'
        return metadata
        
    @staticmethod
    def json_representation(render_json=True):
        """
        if render_json, return the content of static file
        else return a list of PlaceTypes
        """
        # FIXME: return json_file.read() as JSON content
        if render_json:
            json_file = open(settings.FS_CATEGORIES_FILE, 'r')
            return json_file.read()
        else:
            return PlaceType.objects.all()
