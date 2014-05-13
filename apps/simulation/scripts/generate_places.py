from places.models import Place
from django.db import transaction
from clint.textui import progress, colored #Eye candy


class PlaceGenerator(object):
    """
    Generates Places form file places.txt populated with Google Places
    """ 

    def __init__(self):
        self.places_file = 'places.txt'
    
    @transaction.commit_manually
    def run(self):
        try:
            places = open(self.places_file, 'r').readlines()
        except IOError, e:
            print e

        actual_places = []
        for plc in places:
            places.pop()
            places.pop()
            places.pop()
            places.pop() # LNG:
            places.pop() # LAT:
            place_name = places.pop() # NAME:
            places.pop()
            actual_places.append(place_name)

        session_counter = 0
        print colored.white("Generating places:")
        for pls in progress.bar(actual_places):
            place = Place(name = pls)
            session_counter += 1
            place.save()
            
            if session_counter >= 5000:
                session_counter = 0
                transaction.commit()

        transaction.commit()
    
