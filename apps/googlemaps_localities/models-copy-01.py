# -*- coding: utf-8 -*-

import simplejson as json
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from googlemaps_localities import strings, constants

class GoogleMapsAddressComponent(models.Model):
    """
    Implements a Google Maps component address object
    """

    short_name = models.CharField(
        verbose_name=strings.GMAC_SHORT_NAME, 
        max_length=128
    )

    long_name = models.CharField(
        verbose_name=strings.GMAC_LONG_NAME, 
        max_length=128
    )

    formatted_name = models.CharField(
        verbose_name=strings.GMAC_FORMATTED_NAME, 
        max_length=512
    )

    slug = models.SlugField(
        verbose_name=strings.GMAC_SLUG,
        max_length=512,
        blank=True,
        null=True
    )

    component_type = models.CharField(
        verbose_name=strings.GMAC_COMPONENT_TYPE,
        choices=constants.ADDRESS_COMPONENT_TYPE_CHOICES,
        max_length=128
    )

    parent = models.ForeignKey('self',
        verbose_name=strings.GMAC_PARENT,
        blank=True,
        null=True
    )

    location = models.PointField(
        verbose_name=strings.GMAC_LOCATION,
        blank=True,
        null=True
    )

    northeast_bound = models.PointField(
        verbose_name=strings.GMAC_NORTHEAST_BOUND,
        blank=True,
        null=True
    )

    soutwest_bound = models.PointField(
        verbose_name=strings.GMAC_SOUTHWEST_BOUND,
        blank=True,
        null=True
    )

    northeast_viewport = models.PointField(
        verbose_name=strings.GMAC_NORTHEAST_VIEWPORT,
        blank=True,
        null=True
    )

    soutwest_viewport = models.PointField(
        verbose_name=strings.GMAC_SOUTHWEST_VIEWPORT,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        verbose_name=strings.GMAC_CREATED_AT,
        auto_now_add=True
    )


    updated_at = models.DateTimeField(
        verbose_name=strings.GMAC_UPDATED_AT,
        auto_now=True
    )

    class Meta:
        ordering = ('formatted_name','created_at', )
        verbose_name = strings.ADDRESS_COMPONENT
        verbose_name_plural = strings.ADDRESS_COMPONENT_PLURAL

    def __unicode__(self):
        return self.formatted_name

    def save(self, *args, **kwargs):
        if self.slug is None:
            self.slug = self.create_slug()
        return super(GoogleMapsAddressComponent, self).save(*args, **kwargs)

    def create_slug(self):
        elements = self.get_lineage(reverse=True)
        return '/'.join([slugify(e.short_name) for e in elements])

    @staticmethod
    def check_component_type(component_type):
        available_types = dict(constants.ADDRESS_COMPONENT_TYPE_CHOICES).keys()
        return component_type in available_types

    @staticmethod
    def get_or_create(**kwargs):

        klass = GoogleMapsAddressComponent

        # Check component type
        if not klass.check_component_type(kwargs['component_type']):
            return None

        # Params for lookup
        params = {}
        for p in kwargs:
            params[p] = kwargs[p]

        if 'parent__short_name' in params:
            del(params['parent'])

        # Object lookup
        try:
            obj = klass.objects.get(**params)
        except klass.DoesNotExist:
            # Not found, we create it.
            obj = klass(
                short_name=kwargs['short_name'],
                long_name=kwargs['long_name'],
                component_type=kwargs['component_type'],
                parent=kwargs['parent']
            )
            obj.update_formatted_name(commit=False)
            obj.save()

        return obj

    def get_ancestors(self, reverse=False):
        results = []
        current = self.parent
        while current is not None:
            results.append(current)
            current = current.parent
        if reverse:
            results.reverse()
        return results
    
    def get_lineage(self, reverse=False):
        results = []
        results.append(self)
        results.extend(self.get_ancestors())
        if reverse:
            results.reverse()
        return results

    def get_immediate_children(self):
        return GoogleMapsAddressComponent.objects.filter(parent=self)

    def get_all_children(self, allowed_types=[]):
        results = []
        immediate_children = self.get_immediate_children()
        results.extend(immediate_children)
        for child in self.get_immediate_children():
            results.extend(child.get_all_children())
        if len(allowed_types)>0:
            for child in results:
                if child.component_type not in allowed_types:
                    results.remove(child)
        return results

    def update_formatted_name(self, commit=True):
        elements = []
        elements.append(self)
        elements.extend(self.get_ancestors())
        self.formatted_name = ', '.join([e.long_name for e in elements])
        if commit:
            self.save()
        return self.formatted_name

    @staticmethod
    def get_components_from_json(json_string, allowed_types = None):

        if allowed_types is None:
            allowed_types = [
                'locality',
                'administrative_area_level_3',
                'administrative_area_level_2',
                'administrative_area_level_1',
                'country'
            ]

        results = []
        try:
            data = json.loads(json_string)
        except json.decoder.JSONDecodeError:
            return None

        if 'address_components'in data:
            results = data['address_components']
        elif 'results' in data and len(data['results'])>0:
            if 'address_components' in data['results'][0]:
                results = data['results'][0]['address_components']
        
        for e in results:
            allowed = False
            for t in e['types']:
                if t in allowed_types:
                    allowed = True
                    break
            if not allowed:
                results.remove(e)

        return results


    @staticmethod
    def filter_components_below(components, component_type='locality'):
        results = []

        type_found = False
        for c in components:
            if not type_found:
                if component_type in c['types']:
                    type_found = True
                else:
                    continue
            results.append(c)

        return results

    @staticmethod
    def stack_components(components):
        first = None
        current = None
        for c in components:
            if first is None:
                first = c
                current = first
                continue
            else:
                current['parent'] = c
                current = current['parent']
        current['parent'] = None
        return first


    @staticmethod
    def get_or_create_from_json(json_string, max_items=None, type_list=[]):
        results = []
        try:
            data = json.loads(json_string)
        except json.decoder.JSONDecodeError:
            return None

        # Create address components
        records = data['results']
        itemcount = 0
        for record in records:
            components = record['address_components']
            components.reverse()

            obj = None
            current = None
            num_components = len(components)
            for pos, c in enumerate(components):
                if 'types' in c and len(c['types'])>0:
                    if pos + 1 < num_components - 2:
                        next_item = components[pos + 1]
                        current = GoogleMapsAddressComponent.get_or_create(
                            short_name=c['short_name'],
                            long_name=c['long_name'],
                            component_type=c['types'][0],
                            parent__short_name=next_item['short_name'],
                            parent__component_type=next_item['types'][0],
                            parent=current
                        )
                    else:
                        current = GoogleMapsAddressComponent.get_or_create(
                            short_name=c['short_name'],
                            long_name=c['long_name'],
                            component_type=c['types'][0],
                            parent=current
                        )
                else:
                    current = None
                if current is not None:
                    # If only certain types are to be included in the
                    # results, skip items of all the other types.
                    if len(type_list)>0:
                        if current.component_type not in type_list:
                            continue
                    results.append(current)
                    obj = current

            if obj is None:
                continue

            # Add extra fields 
            if 'geometry' in record and 'location' in record['geometry']:
                obj.location = Point(
                    record['geometry']['location']['lat'],
                    record['geometry']['location']['lng']
                )

            if 'geometry' in record and 'bounds' in record['geometry']:
                obj.northeast_bound = Point(
                    record['geometry']['bounds']['northeast']['lat'],
                    record['geometry']['bounds']['northeast']['lng']
                )
                obj.southwest_bound = Point(
                    record['geometry']['bounds']['southwest']['lat'],
                    record['geometry']['bounds']['southwest']['lng']
                )

            if 'viewport' in record['geometry']:
                obj.northeast_bound = Point(
                    record['geometry']['viewport']['northeast']['lat'],
                    record['geometry']['viewport']['northeast']['lng']
                )
                obj.southwest_bound = Point(
                    record['geometry']['viewport']['southwest']['lat'],
                    record['geometry']['viewport']['southwest']['lng']
                )

            obj.save()

            itemcount += 1

            if max_items is not None and itemcount == max_items:
                break

        # Return created objects
        return results

    @staticmethod
    def get_or_create_locality_from_json(json_string):
        results = GoogleMapsAddressComponent.get_or_create_from_json(
            json_string=json_string,
            type_list=['locality'],
            max_items=1
        )
        if results is not None and len(results)>0:
            return results[0]
        else:
            return None
