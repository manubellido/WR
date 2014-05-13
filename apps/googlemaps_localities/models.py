# -*- coding: utf-8 -*-

import simplejson as json
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.template.defaultfilters import slugify
from django.core.exceptions import MultipleObjectsReturned
from googlemaps_localities import settings as localities_settings
from googlemaps_localities import strings, constants
from googlemaps_localities.utils import get_redis_connection
from common.utils.debug import writelog
from rest.utils import render_as_json

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
        unique_together = (
            ('short_name', 'long_name', 'component_type', 'parent', ),
        )

    def __unicode__(self):
        return self.formatted_name

    def save(self, *args, **kwargs):
        if self.slug is None or kwargs.pop('override_slug', False):
            self.slug = self.create_slug()
        result = super(GoogleMapsAddressComponent, self).save(*args, **kwargs)
        if self.parent is not None:
            self.parent.sync_all_children_to_redis()
            self.parent.sync_children_to_redis()
        return result

    def create_slug(self):
        parts = []
        elements = self.get_lineage(reverse=True)
        for e in elements:
            candidate = e.short_name
            if candidate.isdigit():
                candidate = e.long_name
            parts.append(slugify(candidate))
        return '/'.join(parts)

    @staticmethod
    def check_component_type(component_type):
        available_types = dict(constants.ADDRESS_COMPONENT_TYPE_CHOICES).keys()
        return component_type in available_types

    @staticmethod
    def get_or_create(short_name, long_name, component_type, parent=None):

        # Check component type
        if not GoogleMapsAddressComponent.check_component_type(component_type):
            return None

        # Params for lookup
        params = {}
        params['short_name'] = short_name
        params['long_name'] = long_name
        params['component_type'] = component_type
        if parent is not None:
            params['parent'] = parent

        # Object lookup
        try:
            obj = GoogleMapsAddressComponent.objects.get(**params)
        except GoogleMapsAddressComponent.DoesNotExist:
            # Not found, we create it.
            obj = GoogleMapsAddressComponent(
                short_name=short_name,
                long_name=long_name,
                component_type=component_type,
                parent=parent
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

    def get_all_children(self, allowed_types=None):
        allowed_types = allowed_types or []
        results = []
        immediate_children = self.get_immediate_children()
        results.extend(immediate_children)
        for child in immediate_children:
            results.extend(child.get_all_children())
        if len(allowed_types)>0:
            for child in results:
                if child.component_type not in allowed_types:
                    results.remove(child)
        return results

    def get_all_children_seq(self):
        """
        sequencial method homologous to the previous one
        """
        results = []
        queue = []
        children = self.get_immediate_children()
        results.extend(children)
        queue.extend(children)
        while len(queue) > 0:
            node = queue.pop()
            children = node.get_immediate_children()
            results.extend(children)
            queue.extend(children)
        return results

    @staticmethod
    def get_children_from_redis(gmac_id, as_objects=True):
        """
        get all the children on gmac_id from redis DB
        """
        conn = get_redis_connection()
        klass = GoogleMapsAddressComponent
        results = []
        queue = []
        children = klass.get_children_id_list_from_redis_by_pk(gmac_id)
        results.extend(children)
        queue.extend(children)
        while len(queue) > 0:
            node = queue.pop()
            children = klass.get_children_id_list_from_redis_by_pk(node)
            results.extend(children)
            queue.extend(children)
        if as_objects:
            results = klass.objects.filter(pk__in=results)
        return results

    @staticmethod
    def get_all_children_from_redis(gmac_id, as_objects=True):
        """
        get all the children on gmac_id from redis DB, much FASTER
        """
        conn = get_redis_connection()
        klass = GoogleMapsAddressComponent
        results = klass.get_all_children_id_list_from_redis_by_pk(gmac_id)
        if as_objects:
            results = klass.objects.filter(pk__in=results)
        return results   

    @staticmethod
    def get_id_list_from_redis(gmac_id):
        klass = GoogleMapsAddressComponent
        results = []
        results.append(gmac_id)
        results.extend(klass.get_all_children_from_redis(gmac_id, False))
        results = [int(e) for e in results]
        return results

    @staticmethod
    def get_redis_children_key(gmac_id):
        return "%s:%s" % ('gmac_children',gmac_id)

    @staticmethod
    def get_redis_all_children_key(gmac_id):
        return "%s:%s" % ('gmac_all_sons',gmac_id) 

    def sync_children_to_redis(self):
        conn = get_redis_connection()
        key = GoogleMapsAddressComponent.get_redis_children_key(self.pk)
        # First, we make sure the key gets destroyed if it exists
        conn.delete(key)
        # Now we add the keys of the children to the list
        children = self.get_immediate_children()
        for child in children:
            conn.lpush(key, child.pk)

    def sync_all_children_to_redis(self):
        """
        synchronizes all the children to a Redis list
        """
        conn = get_redis_connection()
        key = GoogleMapsAddressComponent.get_redis_all_children_key(self.pk)
        # First, we make sure the key gets destroyed if it exists
        conn.delete(key)
        # Now we add the keys of the children to the list
        children = self.get_all_children_seq()
        for child in children:
            conn.lpush(key, child.pk)

    @staticmethod
    def get_children_id_list_from_redis_by_pk(gmac_id):
        try:
            gmac = GoogleMapsAddressComponent.objects.get(pk=gmac_id)
            conn = get_redis_connection()
            key = GoogleMapsAddressComponent.get_redis_children_key(gmac_id)
            length = conn.llen(key)
            return conn.lrange(key, 0, length)
        except GoogleMapsAddressComponent.DoesNotExist:
            return None

    @staticmethod
    def get_all_children_id_list_from_redis_by_pk(gmac_id):
        """
        returns the list of ids from redis key
        """
        try:
            gmac = GoogleMapsAddressComponent.objects.get(pk=gmac_id)
            conn = get_redis_connection()
            key = GoogleMapsAddressComponent.get_redis_all_children_key(gmac_id)
            length = conn.llen(key)
            return conn.lrange(key, 0, length)
        except GoogleMapsAddressComponent.DoesNotExist:
            return None

    def get_children_id_list_from_redis(self):
        return GoogleMapsAddressComponent.get_children_id_list_from_redis_by_pk(
            self.pk
        )

    def update_formatted_name(self, commit=True):
        elements = []
        elements.append(self)
        elements.extend(self.get_ancestors())
        self.formatted_name = ', '.join([e.long_name for e in elements])
        if commit:
            self.save()
        return self.formatted_name

    def get_short_formatted_name(self):
        lineage = self.get_lineage()
        if len(lineage)>3:
            elements = []
            elements.append(lineage[0].long_name)
            elements.append(lineage[1].long_name)
            elements.append(lineage[-1].long_name)
            return ', '.join(elements)
        else:
            return self.formatted_name

    @staticmethod
    def get_components_from_json(json_string, index=0):

        results = []
        try:
            data = json.loads(json_string)
        except json.decoder.JSONDecodeError:
            return None

        if 'address_components'in data:
            components = data['address_components']
        elif 'results' in data and len(data['results'])>0:
            if 'address_components' in data['results'][index]:
                components = data['results'][index]['address_components']
        else:
            return results

        if not components:
            return results

        for c in components:
            if 'political' in c['types']:
                results.append(c)

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
    def get_component_objects(components=None):
        components = components or []
        results = []
        if len(components)>0 and not 'country' in components[0]['types']:
            components.reverse()
        parent = None
        for c in components:
            obj = GoogleMapsAddressComponent.get_or_create(
                short_name=c['short_name'],
                long_name=c['long_name'],
                component_type=c['types'][0],
                parent=parent
            )
            if obj is not None:
                results.append(obj)
                parent = obj
        # Reverse elements
        results.reverse()
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
    def set_location_data(obj, record):
        if 'geometry' in record and record['geometry'] is None:
            return None
        if 'geometry' in record and 'location' in record['geometry']:
            if record['geometry']['location'] is not None:
                obj.location = Point(
                    record['geometry']['location']['lat'],
                    record['geometry']['location']['lng']
                )

        if 'geometry' in record and 'bounds' in record['geometry']:
            if record['geometry']['bounds'] is not None:
                obj.northeast_bound = Point(
                    record['geometry']['bounds']['northeast']['lat'],
                    record['geometry']['bounds']['northeast']['lng']
                )
                obj.southwest_bound = Point(
                    record['geometry']['bounds']['southwest']['lat'],
                    record['geometry']['bounds']['southwest']['lng']
                )

        if 'viewport' in record['geometry']:
            if record['geometry']['viewport'] is not None:
                obj.northeast_bound = Point(
                    record['geometry']['viewport']['northeast']['lat'],
                    record['geometry']['viewport']['northeast']['lng']
                )
                obj.southwest_bound = Point(
                    record['geometry']['viewport']['southwest']['lat'],
                    record['geometry']['viewport']['southwest']['lng']
                )

        obj.save()

    @staticmethod
    def get_or_create_from_json(json_string, max_items=None, type_list=None):
        type_list = type_list or []
        results = []
        try:
            data = json.loads(json_string)
        except json.decoder.JSONDecodeError:
            return None

        # Create address components
        records = data['results']
        for index, record in enumerate(records):
            try:

                components = \
                    GoogleMapsAddressComponent.get_components_from_json(
                    json_string, index
                )

                objects = GoogleMapsAddressComponent.get_component_objects(
                    components
                )

                # Find wanted objects
                for obj in objects:
                    if obj is None:
                        continue
                    if obj.component_type in type_list and \
                        obj not in results:
                        results.append(obj)

                # Grab geometry / location info
                if (len(objects)> 0) and ('types' in record) \
                        and ('political' in record['types']):
                    GoogleMapsAddressComponent.set_location_data(
                        obj=objects[0],
                        record=record
                    )
            except MultipleObjectsReturned:
                log_path = localities_settings.REVERSE_GEOLOCATION_ERROR_LOG
                json_chunk = render_as_json(records[index])
                writelog(log_path, json_chunk)
                continue

        # Finally, return collected results
        return results


    @staticmethod
    def get_or_create_locality_from_json(json_string):
        results = GoogleMapsAddressComponent.get_or_create_from_json(
            json_string=json_string,
            type_list=[
                'locality',
                'sublocality',
                'administrative_area_level_2',
                'administrative_area_level_1',
                'country'
            ],
            max_items=1
        )
        if results is not None and len(results)>0:
            return results[0]
        else:
            return None
