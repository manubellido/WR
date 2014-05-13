# -*- coding: utf-8 -*-
from os.path import dirname, join, realpath
import foursquare
import time

try:
    import json
except ImportError:
    import simplejson as json

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from user_profile.models import UserProfile 
from places.models import Place, PlaceType
from places.constants import DEFAULT_PLACE_TYPE_ID, FS_API_VERSION
from circuits.models import Circuit, CircuitStop

class CMatcher(object):
    """
    Class 4SQ matcher, matches nextstop scraped places with 4SQ places
    """
    
    def __init__(self, limit=0, line=0):
        """
        Instantiate a client with access_token
        """
        # userless request, suppose to have 5000 queries x hour
        self.client = foursquare.Foursquare(
            client_id=settings.FS_CLIENT_ID, 
            client_secret=settings.FS_CLIENT_SECRET,
            version=FS_API_VERSION
        )
        self.limit = limit
        self.number_lines = line
        
        
    def print_failed_place(self, place_name, circuit=None):
        """
        prints to file the places not found on FS
        """
        filename = realpath(join(
                settings.ROOT_DIR, 
                'apps', 
                'places', 
                'scripts', 
                'not_created_places.txt'
                )
            )       
        FILE = open(filename, 'a')
        FILE.write(place_name)
        if circuit is not None:
            FILE.write('\t')
            FILE.write(circuit.name)
            
        FILE.write('\n')
        FILE.close
    
    
    def search_place(self, query, near=None, ll=None):
        """
        query a place on FS API
        """    
        
        # build params dict
        params = {
            'query':query,
            'near': near,
            'll': ll,
            'limit': '1',
        }
        
        # erase fields with None
        for k, v in params.items():
            if v is None:
                del params[k]

        if self.limit > 4800:
            self.limit = 0
            # sleep for 1 hour
            print "going into sleep for 1 hour ",
            print str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
            time.sleep(3660)
            
        # sleep 4 seconds between requests
        time.sleep(2)
        request_count = 0
        while 1:
            try:
                response = self.client.venues.search(params=params)
                self.limit += 1
                return response
            except:
                # sleep for 60 seconds
                if request_count == 5:
                    print "Too many tries, skip place"
                    request_count = 0
                    return None
                    
                print "Retrying on: " + query
                time.sleep(20)
                request_count += 1
        
        
    def process_search(self, 
        circuit, 
        place_name, 
        lat, 
        lng, 
        location, 
        description
    ):
        """
        invokes search_place and processes the response
        """
        location = location.replace(' ', '-')
        description = description.replace('-', ' ')
        if location == 'The-World' and lat == 'NO-LAT':
            self.print_failed_place(place_name, circuit)
            return
                           
        elif lat == 'NO-LAT' and location is not 'The-World':
            result = self.search_place(
                query=place_name,
                near=location,
            )
                
        elif lat is not 'NO-LAT' and location == 'The-World':
            result = self.search_place(
                query=place_name,
                ll = lat+', '+lng,
            )
                  
        else:
            result = self.search_place(
                query = place_name,
                near = location,
                ll = lat+', '+lng,
            )
            
        if result is None:
            self.print_failed_place(place_name, circuit)
            return
                
        cat_id = None
        find_venue = False
        if 'venues' in result:
            for field in result['venues']:
                place_name = field['name']
                place_id = field['id']
                find_venue = True
                try:
                    place_phone = field['contact']['phone']
                except KeyError:
                    place_phone = None
                try:
                    place_address = field['location']['address']
                except KeyError:
                    place_address = None
                try:
                    latitude = field['location']['lat']
                    longitud = field['location']['lng']
                    place_coords = Point(latitude, longitud)
                except KeyError:
                    # FIXME: place_coords should not default to 0,0
                    # but for now place_coords is mandatory field on DB
                    place_coords = Point(0,0)
                        
                for elem in field['categories']:
                    cat_id = elem['id']
                if cat_id is None:
                    cat_id = DEFAULT_PLACE_TYPE_ID
                    
        if find_venue:
            # see if already in DB
            try:
                pl = Place.objects.get(place_id = place_id)
            except Place.DoesNotExist:
                pl = Place()
                pl.name = place_name
                pl.place_id = place_id
                pl.coordinates = place_coords
                if place_phone is not None:
                    pl.phone_number = place_phone
                if place_address is not None:
                    pl.address = place_address
                pl.save()
                try:
                    pt = PlaceType.objects.get(place_type_id=cat_id)
                except PlaceType.DoesNotExist:
                    pt = PlaceType.objects.all()[0]
                pl.place_type.add(pt)
                pl.save()

            cs = CircuitStop()
            cs.circuit = circuit
            cs.place = pl
            cs.description = description
            cs.save()
        
        else:
            self.print_failed_place(place_name, circuit)
            return
    
    
    def create_or_find_author(self, username):
        """
        returns a User object, rather finding it or creating it
        """
        try:
            us = User.objects.get(first_name=username)
        except User.DoesNotExist:
            us = UserProfile.create_user_with_tokens(
                username,
                '', # username
                username,
                username
            )      
        return us
        
        
    def read_from_file(self, filename):
        """
        reads places from file
        """
        with open(filename, 'r') as FILE:
            for line in FILE:
                #line = FILE.readline()
                # eliminate \n at end
                line = line.strip()
                self.number_lines += 1
                if line == '@#':
                    guide_title = FILE.next().strip()
                    self.number_lines += 1
                    guide_title = guide_title.replace('-', ' ')
                    guide_author = FILE.next().strip()
                    self.number_lines += 1
                    # returns a user, finding it or creating it
                    author = self.create_or_find_author(guide_author)
                    location = FILE.next().strip()
                    self.number_lines += 1
                    location = location.split('\t')
                    location = location[-1]
                    description = FILE.next().strip().replace('-', ' ')
                    self.number_lines += 1
                    # create circuit
                    # FIXME: decription migth be 'NO-DESCRIPTION' and
                    # category should be somehow matched to a proper category
                    try:
                        new_ct = Circuit.objects.get(
                            name=guide_title,
                            author=author,
                        )
                    except Circuit.DoesNotExist:
                        new_ct = Circuit(
                            name=guide_title,
                            category=4,
                            author=author,
                            description=description[:399],
                            published=True,
                            source=3,
                        )
                    print 'Creating circuit ' + guide_title
                    new_ct.save()
                    # move line 1 position forward so place can read from here
                    line = FILE.next().strip()
                    self.number_lines += 1
                
                # a place
                fields = line.split('\t')
                place_name = fields[0].replace('-', ' ')
                lat = fields[1]
                lng = fields[2]
                try:
                    desc = fields[3]
                except IndexError:
                    dec = ''
                # invoke process_search and pass fields
                self.process_search(
                    circuit=new_ct,
                    place_name=place_name, 
                    lat=lat, 
                    lng=lng, 
                    location=location,
                    description=desc
                )
                    
                    
    def clean_empty_circuits(self):
        """
        deletes the circuits with no places
        """
        pass
        
    def run(self):
        filename = realpath(join(
            settings.ROOT_DIR, 
            'apps', 
            'places', 
            'scripts', 
            'place_per_guide.txt'
            )
        )            
        self.read_from_file(filename) 
    
# ===========================     M A I N     ===============================

if __name__ == "__main__":
    cm = CMatcher()
    cm.run()

