# -*- coding: utf-8 -*-

import re
from ordereddict import OrderedDict

from django import forms
from django.contrib.gis.geos import Point

from common.utils.strings import multiple_whitespace_to_single_space
from topics.models import Topic
from places.models import Place, PlaceType
from places.constants import DEFAULT_PLACE_TYPE_ID
from circuits.models import (Circuit, CircuitStop)
from circuits.utils import CircuitCategory
from circuits import constants
from circuits import strings
from googlemaps_localities.models import GoogleMapsAddressComponent as GMAC
from rest.forms import PatchModelForm


rx_n = re.compile('/n+')


class CircuitCreationControllerForm(forms.Form):

    name = forms.CharField(
        max_length=256
    )

    category = forms.ChoiceField(
        choices=constants.CIRCUIT_CATEGORY_CHOICES
    )

    topics = forms.CharField(
        max_length=512,
        required=False
    )

    description = forms.CharField(
        max_length=512,
        widget=forms.Textarea(attrs={'rows': '', 'cols': '', 'maxlength': '512'}),
        required=False,
    )

    adult_content = forms.BooleanField(
        required=False
    )

    def clean_topics(self):
        topics = self.cleaned_data.get('topics', []).strip()
        if topics:
            topics = ', '.join(Topic.parse_names(topics))
        return topics

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        desc = re.sub(rx_n, '<br>', desc)
        return desc

    def process_objects(self, author):
        # Circuit
        circuit = Circuit(
            name=self.cleaned_data.get('name', ''),
            category=self.cleaned_data.get('category', ''),
            description=self.clean_description(),
            author=author,
            adult_content=self.cleaned_data['adult_content']
        )

        circuit.save()
        # Topics
        new_topics = []
        all_topics = []
        topic_names = Topic.parse_names(self.cleaned_data('topics', []))
        for tn in topic_names:
            if not Topic.exists(tn):
                topic = Topic.get_or_create(tn)
                new_topics.append(topic)
            else:
                topic = Topic.get_by_name(tn)
            all_topics.append(topic)
        multiple = False
        if len(new_topics) > 0:
            multiple = True
        # Add topics to circuit
        for topic in all_topics:
            circuit.topics.add(topic)
        circuit.save()
        return {
            'circuit': circuit,
            'all_topics': all_topics,
            'new_topics': new_topics,
            'multiple': multiple
        }

class CircuitPatchControllerForm(PatchModelForm):
    class Meta:
        model = Circuit


class CircuitUpdateControllerForm(CircuitCreationControllerForm):

    circuit_id = forms.IntegerField(
        min_value=1
    )

    def clean_circuit_id(self):
        circuit_id = self.cleaned_data.get('circuit_id')
        if Circuit.objects.filter(pk=circuit_id).exists():
            return circuit_id
        else:
            raise forms.ValidationError(strings.NON_EXISTANT_CIRCUIT)

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        desc = re.sub(rx_n, '<br>', desc)
        return desc

    def process_objects(self, author):
        # Circuit
        circuit = Circuit.objects.get(pk=self.cleaned_data.get('circuit_id'))
        circuit.name = self.cleaned_data.get('name', '')
        circuit.category = self.cleaned_data.get('category',
            constants.DEFAULT_CIRCUIT_CATEGORY)
        circuit.description = self.clean_description()
        circuit.adult_content = self.cleaned_data['adult_content']

        circuit.author = author
        circuit.save()

        # Topics
        new_topics = []
        all_topics = []
        topic_names = Topic.parse_names(self.cleaned_data.get('topics', []))
        for tn in topic_names:
            if not Topic.exists(tn):
                topic = Topic.get_or_create(tn)
                new_topics.append(topic)
            else:
                topic = Topic.get_by_name(tn)
            all_topics.append(topic)
        multiple = False
        if len(new_topics) > 0:
            multiple = True
        # Remove all previous topics
        circuit.topics.clear()
        # Add topics to circuit
        for topic in all_topics:
            circuit.topics.add(topic)
        circuit.save()
        return {
            'circuit': circuit,
            'all_topics': all_topics,
            'new_topics': new_topics,
            'multiple': multiple
        }


class CircuitPictureControllerForm(forms.ModelForm):

    class Meta:
        model = Circuit
        fields = ('picture', 'id')

    def process_objects(self, author, circuit_id):
        # Circuit
        circuit = Circuit.objects.get(pk=circuit_id)
        circuit.picture = self.cleaned_data.get('picture')
        circuit.save()
        return circuit


class CircuitCollectionFilterForm(forms.Form):
    """
    Validates the fields limit and offset or catches them from constants
    """

    limit = forms.IntegerField(
        min_value=1,
        required=False
    )

    offset = forms.IntegerField(
        min_value=0,
        required=False
    )

    category = forms.CharField(
        min_length=1,
        max_length=24,
        required=False
    )

    gmac_id = forms.IntegerField(
         min_value=1,
        required=False       
    )

    gmac_slug = forms.CharField(
        min_length=1,
        max_length=24,
        required=False
    )

    def clean_category(self):
        category = self.cleaned_data.get('category').upper()
        acceptable_values = []
        keys = constants.CIRCUIT_CATEGORY_CHOICES.keys()
        values = [str(v) for v in constants.CIRCUIT_CATEGORY_CHOICES.values()]
        acceptable_values.extend(keys)
        acceptable_values.extend(values)
        if len(category) == 0 or (category in acceptable_values):
            return category
        else:
            raise forms.ValidationError(
                strings.UNKNOWN_CATEGORY_VALUE % category
            )

    def category_is_numeric(self):
        category = self.cleaned_data.get('category')
        try:
            category = int(category)
            return True
        except ValueError:
            return False

    def category_is_alphanumeric(self):
        category = self.cleaned_data.get('category')
        return len(category)>0 and (not self.category_is_numeric())

    def clean_gmac_id(self):
        gmac_id = self.cleaned_data.get('gmac_id')
        if gmac_id is None:
            return None
        else:
            if GMAC.objects.filter(pk=gmac_id).exists():
                return gmac_id
            else:
                raise forms.ValidationError(
                    strings.UNKNOWN_GMAC % {'gmac': gmac_id}
                )

    def clean_gmac_slug(self):
        gmac_slug = self.cleaned_data.get('gmac_slug').strip()
        if gmac_slug == '':
            return None
        else:
            gmacs = GMAC.objects.filter(slug=gmac_slug)
            if gmacs.exists():
                return gmac_slug
            else:
                raise forms.ValidationError(
                    strings.UNKNOWN_GMAC % {'gmac': gmac_slug}
                )             

    def get_circuits(self):
        """
        Returns a Queryset containing the circuits to display on
        CircuitCollection
        """
        limit = self.cleaned_data.get('limit')
        offset = self.cleaned_data.get('offset')
        category = self.cleaned_data.get('category')
        gmac_id = self.cleaned_data.get('gmac_id')
        gmac_slug = self.cleaned_data.get('gmac_slug')

        if limit is None:
            limit = constants.API_DEFAULT_CIRCUITS_LIMIT
        if offset is None:
            offset = constants.API_DEFAULT_CIRCUITS_OFFSET

        # try to filter circuit by GMAC
        if gmac_id is not None:
            gmac = GMAC.objects.get(pk=gmac_id)
            circuits = Circuit.filter_by_gmac(gmac)

        # try to filter by gmac_slug
        elif gmac_slug is not None:
            gmacs = GMAC.objects.filter(slug=gmac_slug)
            circuits = Circuit.filter_by_gmacs(gmacs)
        # if not filtered by GMAC then filter by any other criteria
        else:
            circuits = Circuit.objects.all()
            circuits = circuits.order_by('-created')

        if category is not None and len(category)>0:

            if self.category_is_alphanumeric():
                category = CircuitCategory(category)
                category = category.get_value()

            circuits = circuits.filter(category=category)

        return circuits[offset:offset + limit]


class CircuitStopCreationControllerForm(forms.Form):

    name = forms.CharField(
        max_length=256
    )

    place_id = forms.CharField(
        max_length=32,
        required=False
    )

    place_type_id = forms.CharField(
        max_length=32,
        required=True
    )

    lat = forms.FloatField(
        min_value=-90.0,
        max_value=90.0
    )

    lng = forms.FloatField(
        min_value=-180.0,
        max_value=180.0
    )

    address = forms.CharField(
        max_length=512,
        required=False
    )

    crossStreet = forms.CharField(
        max_length=256,
        required=False
    )

    phone_number = forms.CharField(
        max_length=24,
        required=False
    )

    website = forms.URLField(
        required=False
    )

    twitter = forms.CharField(
        max_length=24,
        required=False
    )

    description = forms.CharField(
        max_length=512,
        widget=forms.Textarea(attrs={'maxlength': '400',
            'rows': '',
            'cols': ''}),
        required=False,
    )

    picture = forms.ImageField(
        required=False
    )

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        name = multiple_whitespace_to_single_space(name).strip()
        return name

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        desc = re.sub(rx_n, '<br>', desc)
        return desc

    def process_objects(self, circuit):
        results = OrderedDict()
        # multiple = true if creating a place and a CircuitStop
        results['multiple'] = False
        # conflict = CircuitStop with this place already exists
        results['conflict'] = False
        new_place = False

        place = None

        place_id = self.cleaned_data.get('place_id', None)
        print type(place_id)
        if place_id != '':
            try:
                place = Place.objects.get(place_id=place_id)
            except Place.DoesNotExist:
                place = None

        # Enter here if query did not returned a Place
        if place is None:
            # Mandatory fields
            place = Place()
            place.name = self.cleaned_data.get('name', '')
            place.coordinates = Point(
                self.cleaned_data.get('lat'),
                self.cleaned_data.get('lng')
            )
            if place_id is not None:
                place.place_id = place_id
            else:
                # TODO handle case when no place_id is passed
                pass
            # Optional fields
            if 'address' in self.cleaned_data:
                place.address = self.cleaned_data.get('address', '')
            if 'phone_number' in self.cleaned_data:
                place.phone_number = self.cleaned_data.get('phone_number', '')
            if 'website' in self.cleaned_data:
                place.website = self.cleaned_data.get('website', '')
            if 'crossStreet' in self.cleaned_data:
                place.crossStreet = self.cleaned_data.get('crossStreet', '')
            if 'twitter' in self.cleaned_data:
                place.twitter = self.cleaned_data.get('twitter', '')
            # get place_type from db or default
            try:
                place_type = PlaceType.objects.get(
                    place_type_id=self.cleaned_data.get('place_type_id')
                )
            except PlaceType.DoesNotExist:
                place_type = PlaceType.objects.get(
                    place_type_id=DEFAULT_PLACE_TYPE_ID
                )

            place = Place.new_place_save(place, place_type)

            # Sync new Place with MongoDB
            # check_mongo(place)
            # Setting the new place flag to True
            new_place = True

        # Check if the place object has not yet been included in
        # a circuit stop that is part of the circuit
        if circuit.circuit_stops.filter(place=place).exists():
            # There is a conflict with the current state of the
            # resource since there already exists a circuit stop
            # referring to that place
            results['conflict'] = True
            return results

        # Creating a circuit stop for the place
        circuit_stop = CircuitStop(
            circuit=circuit,
            place=place,
            description=self.clean_description(),
            picture=self.cleaned_data.get('picture')
        )

        circuit_stop.save()
        # Now we add it to the circuit
        circuit.circuit_stops.add(circuit_stop)
        circuit.save()
        # Create objects dictionary
        results['circuit_stop'] = circuit_stop
        if new_place:
            results['place'] = place
            results['multiple'] = True
        # Return results dictionary
        return results


class CircuitPublicationStatusForm(forms.Form):

    published = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            self.instance = kwargs.pop('instance')
        return super(CircuitPublicationStatusForm, self).__init__(
            *args, **kwargs
        )

    def clean_published(self):
        if self.instance.published != self.cleaned_data.get('published'):
            return self.cleaned_data.get('published')
        else:
            if self.instance.published:
                message = strings.CIRCUIT_ALREADY_PUBLISHED
            else:
                message = strings.CIRCUIT_ALREADY_UNPUBLISHED
            raise forms.ValidationError(message)

    def update_publication_status(self):
        self.instance.published = self.cleaned_data.get('published')
        self.instance.save()
        return self.instance


class CircuitStopUpdateControllerForm(forms.ModelForm):

    class Meta:
        model = CircuitStop
        fields = ('description', 'picture', )

    def get_updated_fields(self):
        results = []
        possible_fields = (
            'description',
            'picture'
        )
        #FIXME: Correctly detect when the picture gets updated
        for p in possible_fields:
            if p in self.cleaned_data:
                results.append(p)
        return results
