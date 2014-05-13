# -*- coding: utf-8 -*-

import foursquare
import time
import urllib2
import random
from os.path import join, realpath

from django.conf import settings
from django.core.files import File
from places.constants import FS_API_VERSION
from circuits.models import Circuit


class FSPhoto(object):
    """
    Class 4SQ matcher, matches nextstop scraped places with 4SQ places
    """
    def __init__(self, limit=0):
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
                 
    def search_place_photo(self, venue_id, limit=1, group='venue'):
        """
        query a venue photo on FS API
        """    
        # build params dict
        params = {
            'limit':limit,
            'group': group,
        }
    
        if self.limit > 4800:
            self.limit = 0
            # sleep for 1 hour
            print "going into sleep for 1 hour ",
            print str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min)
            time.sleep(3660)
            
        # sleep 4 seconds between requests
        request_count = 0
        while 1:
            try:
                self.limit += 1
                response = self.client.venues.photos(
                    VENUE_ID=venue_id,
                    params=params
                )
                return response
            except:
                # sleep for 60 seconds
                if request_count == 5:
                    print "Too many tries, skip venue photo"
                    request_count = 0
                    return None
                    
                print "Retrying on: " + venue_id
                time.sleep(20)
                request_count += 1
                         
    def process_empty_circuits(self, circuits):
        """
        processes all the circuits that has no associated photo with them   
        """
        for ct in circuits:
            # get 1 place and pass to process photo
            places_ids = []
            places = ct.get_places()
            for pl in places:
                places_ids.append(pl.place_id)
                
            self.process_photo(ct, places_ids)
               
    def process_photo(self, circuit, places_ids):
        """
        invokes search_place and processes the response
        """
        for pk in places_ids:
            result = self.search_place_photo(venue_id=pk)                
            if result is None:
                # could not retrieve anything
                return
        
            if 'photos' in result:
                for field in result['photos']['items']:
                    url = field['prefix'] + 'original' + field['suffix']
                    self.download_photo(url, circuit)
                    return
         
    def download_photo(self, url, circuit):
        """ handles the download of a photo and uploads it """
        downloaded_photo = urllib2.urlopen(url)
        # save the file with the circuit.name
        photo_name = circuit.author.username + str(random.randint(1,100000))
        # append extension of the picture
        photo_name += '.' + url[-3:]
        # open in location /data/nextstop_photos
        photo_file = realpath(join(
                settings.ROOT_DIR, 
                'data', 
                'nextstop_photos',  
                photo_name
                )
            )
        saved_photo = open(photo_file,'wb')
        saved_photo.write(downloaded_photo.read())
        saved_photo.close()

        # open photo file and save to field picture
        circuit.picture.save(photo_name, File(open(photo_file, 'r')))
        circuit.save()

          
    def run(self):
        """ Start execution """
        circuits = Circuit.objects.filter(source=3)
        no_photo_circuits = []
        for circuit in circuits:
            if not circuit.picture:
                no_photo_circuits.append(circuit)
              
        self.process_empty_circuits(no_photo_circuits)
