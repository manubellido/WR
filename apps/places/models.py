# -*- coding: utf-8 -*-

from ordereddict import OrderedDict
import requests
import datetime

try:
    import json
except ImportError:
    import simplejson as json

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings

from django_countries import CountryField

from rest.utils import render_as_json
from common.models import AuditableModel
from common.datastructures import Enumeration
from places import constants, strings
from places.constants import DEFAULT_PLACE_TYPE_ID, FS_API_VERSION

from googlemaps_localities.models import GoogleMapsAddressComponent

class FSCountry(AuditableModel):
    """
    Foursquare Country entity
    """

    name = models.CharField(
        verbose_name=strings.FS_COUNTRY_NAME,
        max_length=256,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = strings.FS_COUNTRY_VERBOSE_NAME
        verbose_name_plural = strings.FS_COUNTRY_VERBOSE_NAME_PLURAL
        
    def get_states(self):
        """
        Returns a QuerySet of the states that belong to this country
        """
        return self.states.all()

    @staticmethod
    def exists(country_name):
        results = FSCountry.objects.filter(name=country_name)
        return results.exists()

    @staticmethod
    def create(country_name):
        obj = FSCountry(name=country_name)
        obj.save()
        return obj


class FSState(AuditableModel):
    """
    Foursquare State entity
    """

    name = models.CharField(
        verbose_name=strings.FS_STATE_NAME,
        max_length=256,
    )

    country = models.ForeignKey(FSCountry,
        verbose_name=strings.FS_STATE_COUNTRY,
        related_name='states',
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = strings.FS_STATE_VERBOSE_NAME
        verbose_name_plural = strings.FS_STATE_VERBOSE_NAME_PLURAL
        
    def get_cities(self):
        """
        Returns a QuerySet of the cities that belong to this state
        """
        return self.cities.all()

    @staticmethod
    def exists(state_name, country):
        results = FSState.objects.filter(
            name=state_name,
            country=country
        )
        return results.exists()

    @staticmethod
    def create(state_name, country):
        obj = FSState(name=state_name, country=country)
        obj.save()
        return obj


class FSCity(AuditableModel):
    """
    Foursquare City entity
    """

    name = models.CharField(
        verbose_name=strings.FS_CITY_NAME,
        max_length=256,
    )

    state = models.ForeignKey(FSState,
        verbose_name=strings.FS_CITY_STATE,
        related_name='cities', 
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = strings.FS_CITY_VERBOSE_NAME
        verbose_name_plural = strings.FS_CITY_VERBOSE_NAME_PLURAL

    def get_state_name(self):
        """
        Returns the name of the state to which this city belongs
        """
        return self.state.name
        
    def get_country_name(self):
        """
        Returns the name of the country to which this city belongs
        """
        return self.state.country.name
        
    def get_state_obj(self):
        """
        Returns the state to which this city belongs
        """
        return self.state
    
    def get_country_obj(self):
        """
        Returns the country to which this city belongs
        """
        return self.state.country
        
    def get_all_places(self):
        """
        Returns a QuerySet with all the places in this city
        """
        return self.places.all()

    @staticmethod
    def exists(city_name, state):
        results = FSCity.objects.filter(
            name=city_name,
            state=state
        )
        return results.exists()

    @staticmethod
    def create(city_name, state):
        obj = FSCity(name=city_name, state=state)
        obj.save()
        return obj

    @staticmethod
    def get_or_create_with_names(city_name, state_name, country_name):
        if FSCountry.exists(country_name):
            country = FSCountry.objects.get(name=country_name)
        else:
            country = FSCountry.create(country_name)
        if FSState.exists(country_name, country):
            state = FSState.objects.get(name=state_name, country=country)
        else:
            state = FSState.create(state_name, country)

        if FSCity.exists(city_name, state):
            city = FSCity.objects.get(name=city_name, state=state)
        else:
            city = FSCity.create(city_name, state)
        return city

    def get_formatted_name(self):
        return u'%s, %s, %s' % (
            self.name,
            self.get_state_name(),
            self.get_country_name()
        )
       

class PlaceType(models.Model):
    """
    Foursquare place_type model:
    parent_id, id, name, pluralName, shortName, 
    icon: prefix, sizes, name(image_format);
    """
    
    # Relationship with self as a tree of PlaceTypes
    parent = models.ManyToManyField("self",
        verbose_name=strings.PLACETYPE_RELATION,
        related_name='subtypes',
        null=True,
        blank=True
    )
    
    # PK field, just like in Foursquare
    place_type_id = models.CharField(
        primary_key=True,
        max_length=32
    )
    
    name = models.CharField(
        verbose_name=strings.PLACETYPE_NAME,
        max_length=256,
    )
    
    pluralName = models.CharField(
        verbose_name=strings.PLACETYPE_PLURALNAME,
        max_length=256,
    )
    
    shortName = models.CharField(
        verbose_name=strings.PLACETYPE_SHORTNAME,
        max_length=256,
    )
    
    icon_prefix = models.CharField(
        verbose_name=strings.PLACETYPE_PREFIX,
        max_length=256,
    )
    
    icon_sizes = models.CharField(
        verbose_name=strings.PLACETYPE_SIZES,
        max_length=128,
    )
    
    icon_name = models.CharField(
        verbose_name=strings.PLACETYPE_ICONNAME,
        max_length=8,
    )
    
    def __unicode__(self):
        return u'%s' % (self.name,)

    class Meta:
        verbose_name = strings.PLACETYPE_VERBOSE_NAME
        verbose_name_plural = strings.PLACETYPE_VERBOSE_NAME_PLURAL

    def get_icon_sizes(self):
        sizes = self.icon_sizes.split(',')
        return [s.strip() for s in sizes]

    def get_icon_urls(self):
        results = []
        for size in self.get_icon_sizes():
            url = ''.join([self.icon_prefix, size, self.icon_name])
            results.append(url)
        return results

    def get_icon_dict(self):
        results = OrderedDict()
        for size in self.get_icon_sizes():
            url = ''.join([self.icon_prefix, size, self.icon_name])
            results[size] = url
        return results

    def get_icon(self):
        icon_urls = self.get_icon_urls()
        if len(icon_urls)>0:
            return icon_urls[0]
        else:
            return None
        
    def get_json_representation(self, render_json=True):
        #FIXME: Eventually move to the resource class when implemented
        document = OrderedDict()
        document['place_type_id'] = self.place_type_id
        document['name'] = self.name
        document['plural_name'] = self.pluralName
        document['short_name'] = self.shortName
        # Icons
        document['icons'] = OrderedDict()
        document['icons']['default'] = self.get_icon()
        document['icons']['sizes'] = self.get_icon_dict()
        if render_json:
            return render_as_json(document)
        else:
            return document
        
    def get_subtypes(self):
        """
        Returns all subtypes or sons of self
        """
        return self.subtypes.all()

    def get_restful_url(self):
        return '%s%s' % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('place_type_resource', kwargs={'place_type_id':self.place_type_id})
        )

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = self.name
        metadata['type'] = 'application/json'
        return metadata
        
    @staticmethod
    def populate_from_api():
        # helper script to process place categories from FS
        from places.scripts.FS_utils import venue_cat_parser
        """
        populates the table model in DB from filename
        """
        categories = venue_cat_parser()
        for row in categories:         
            pt = PlaceType()
            pt.place_type_id = row[1]
            pt.name = row[2]
            pt.pluralName = row[3]
            pt.shortName = row[4]
            pt.icon_prefix = row[5]
            pt.icon_sizes = row[6]
            pt.icon_name = row[7]
            pt.save()
            if row[0] is not None:
                parent = PlaceType.objects.get(place_type_id = row[0])
                pt.parent.add(parent)
                
        return len(categories)
        
    @staticmethod
    def get_types_enum():
        """
        Returns an OrderedDict with each type
        """
        place_types = []
        categories = PlaceType.objects.all()
        counter = 1
        # TODO return as hierarchy
        for cat in categories:
            row = (counter, cat.name)
            place_types.append(row)
            counter += 1
            
        return place_types


class Place(models.Model):
    """
    Place base class. Atributes as Foursquare
    """
    
    # PK field, just like in Foursquare
    place_id = models.CharField(
        primary_key=True,
        max_length=32
    )
    
    name = models.CharField(
        verbose_name=strings.PLACE_NAME,
        max_length=256,
    )    
    
    coordinates = models.PointField(
        verbose_name=strings.PLACE_COORDINATES,
    )

    # Foursquare place_type
    place_type = models.ManyToManyField(
        PlaceType,
        verbose_name=strings.PLACE_TYPE,
        related_name='placetype_places',
    )
    
    city = models.ForeignKey(
        FSCity,
        verbose_name=strings.PLACE_CITY,
        related_name='places',
        null=True,
        blank=True,
    )

    locality = models.ForeignKey(
        GoogleMapsAddressComponent,
        verbose_name=strings.PLACE_LOCALITY,
        related_name='places',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    
    crossStreet = models.CharField(
        verbose_name=strings.PLACE_CROSSSTREET,
        max_length=256,
        null=True,
        blank=True,       
    )

    address = models.TextField(
        verbose_name=strings.PLACE_ADDRESS,
        blank=True,
        null=True,
    )

    phone_number = models.CharField(
        verbose_name=strings.PLACE_PHONE_NUMBER,
        max_length=24,
        blank=True,
        null=True,
    )
    
    twitter = models.CharField(
        verbose_name=strings.PLACE_TWITTER_ACCOUNT,
        max_length=24,
        blank=True,
        null=True,
    )

    website = models.URLField(
        verbose_name=strings.PLACE_WEBSITE,
        blank=True,
        null=True,
    )

    country = CountryField(
        verbose_name=strings.PLACE_COUNTRY,
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return u'%s' % (self.name,)

    class Meta:
        verbose_name = strings.PLACE_VERBOSE_NAME
        verbose_name_plural = strings.PLACE_VERBOSE_NAME_PLURAL
    
    @staticmethod   
    def response_200(resp):
        return resp.status_code >= 200 and resp.status_code < 300
    
    @staticmethod
    def response_409(resp):
        return resp.status_code == 409

    def get_place_type(self):
        if self.place_type.count() > 0:
            return self.place_type.all()[0]
        else:
            #TODO: returning a generic place_type by now
            return PlaceType.objects.get(pk=DEFAULT_PLACE_TYPE_ID)

    @staticmethod
    def get_results(place_data):
        """
        Makes a post request to FS API to try adding a new venue/place
        """        
        # URL to add venues to FS
        url = 'https://api.foursquare.com/v2/venues/add?oauth_token='
        url += settings.OAUTH_TOKEN
        url += '&v=' + FS_API_VERSION

        # execute request
        resp = requests.post(url, params=place_data)
        return resp
    
    @staticmethod 
    def save_to_FS(place, place_type):
        """
        Tries to save Place to FS through API
        """
        lat_lng = str(place.coordinates.x) + ',' + str(place.coordinates.y)
        params = {
            # mandatory fields
            'name': place.name,
            'll': lat_lng,
            # optional fields, check if exist
            'address': place.address,
            'crossStreet': place.crossStreet,
            'city': place.get_city_name(),
            'state': place.get_state_name(),
            'phone': place.phone_number,
            'twitter': place.twitter,
            'primaryCategoryId': place_type.pk,
            'url': place.website,
        }
        # delete keys that are None
        for k, v in params.items():
            if v is None:
                del params[k]
        # get results
        response = Place.get_results(params)
        if Place.response_200(response):
            return json.loads(response.text)
        # handle repetitive place insertion attempt    
        elif Place.response_409(response):
            results = json.loads(response.text)
            if 'response' in results and \
                'ignoreDuplicatesKey' in results['response']:
                dup_key = results['response']['ignoreDuplicatesKey']
                params['ignoreDuplicatesKey'] = dup_key
                params['ignoreDuplicates'] = True
                response = Place.get_results(params)
                return json.loads(response.text)
        else:
            # something else went wrong
            return False
    
    @staticmethod
    def new_place_save(new_place, place_type):
        """
        wrapps all the logic of saving a new place 1st fo 4SQ, then
        get the id of new 4SQ place and save to local DB
        """
        import foursquare
        # search place in 4SQ
        client = foursquare.Foursquare(
            client_id=settings.FS_CLIENT_ID, 
            client_secret=settings.FS_CLIENT_SECRET,
            version=FS_API_VERSION
        )
        # build params dict
        params = {
            'query':new_place.name.encode('utf-8'),
            'll': '%s, %s' % (
                new_place.coordinates.x, 
                new_place.coordinates.y)
            ,
            'limit': '1',
        }
        # query 4SQ API
        result = client.venues.search(params=params)
        find_venue = False
        if 'venues' in result:
            for field in result['venues']:
                place_id = field['id']
                find_venue = True
        
        # in case venue was found on 4SQ
        if find_venue:       
                new_place.place_id = place_id
                new_place.save()
                new_place.place_type.add(place_type)
                new_place.save()     
                # return new created place
                return new_place
                
        # in case venue is not even on 4SQ
        else:
            try:
                # Save new venue to FS
                result = Place.save_to_FS(new_place, place_type)
                #print result
                if 'response' in result and 'venue' in result['response']:
                    for field in result['response']['venue']:
                        new_place.place_id = field['id']
                
            except:
                import uuid
                temp_id = str(uuid.uuid4())
                temp_id = temp_id.replace('-','')
                new_place.place_id = temp_id

            new_place.save()
            new_place.place_type.add(place_type)
            new_place.save()
            return new_place

            
    def get_restful_url(self):
        return '%s%s' % (
            settings.API_V1_PREFIX.rstrip('/'),
            reverse('place_resource', kwargs={'place_id':self.place_id})
        )

    def get_restful_link_metadata(self, rel='alternate'):
        metadata = OrderedDict()
        metadata['href'] = self.get_restful_url()
        metadata['rel'] = rel
        metadata['title'] = self.name
        metadata['type'] = 'application/json'
        return metadata

    def get_coordinates_subdoc(self):
        coords = OrderedDict()
        coords['lat'] = self.coordinates.x
        coords['lng'] = self.coordinates.y
        return coords

    def get_coordinates_string(self):
        return '%s,%s' % (
            self.coordinates.x,
            self.coordinates.y
        )
        
    def get_country(self):
        """
        Return the country to which this place belongs
        """
        return self.city.get_country_obj()
     
    def get_country_name(self):
        return self.city.get_country_obj.name if self.city else ''
                
    def get_state(self):
        """
        Return the state to which this place belongs
        """
        return self.city.get_state_obj() if self.city else ''
        
    def get_state_name(self):
        return self.city.get_state_obj().name if self.city else ''
    
    def get_city(self):
        """
        Return the city to which this place belongs
        """
        return self.city
        
    def get_city_name(self):
        return self.city.name if self.city else ''

    @property
    def lat(self):
        return self.coordinates.x

    @property
    def lng(self):
        return self.coordinates.y
        
     
class DonePlace(AuditableModel):
    """
    Relation between places and users, where users
    explicitly mark a place as visited or done
    """

    place = models.ForeignKey(Place,
        verbose_name=strings.DONE_PLACE_PLACE,
        related_name='done_place_records'
    )

    user = models.ForeignKey(User,
        verbose_name=strings.DONE_PLACE_USER,
        related_name='done_place_records'
    )

    ipaddr = models.IPAddressField(
        verbose_name=strings.DONE_PLACE_IPADDR,
        null=True,
        blank=True
    )

    coordinates = models.PointField(
        verbose_name=strings.DONE_PLACE_COORDINATES,
        null=True,
        blank=True
    )

    created_inplace = models.NullBooleanField(
        verbose_name=strings.DONE_PLACE_CREATED_INPLACE,
        null=True,
        blank=True
    )

    def __unicode__(self):
        return strings.DONE_PLACE_UNICODE % {
            'user':self.user.get_full_name(), 
            'place':self.place.name,
        }
        

    class Meta:
        verbose_name = strings.DONE_PLACE_VERBOSE_NAME
        verbose_name_plural = strings.DONE_PLACE_VERBOSE_NAME_PLURAL
        unique_together = (('user', 'place'), )


