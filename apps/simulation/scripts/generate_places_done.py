import random
from circuits.models import Circuit
from visits.models import Visit
from django.contrib.auth.models import User
from django.db import transaction
from places.models import DonePlace, Place
from clint.textui import progress, colored #Eye candy

class PlaceDoneGenerator(object):
    """
    Simulates the probability of a user marking
    a place as visited phisically, done
    """

    @transaction.commit_manually
    def run(self):
        # Get al users from DB
        all_users = User.objects.all()[1:]

        circuit_percent = 5
        percentage = 1
        session_counter = 0
        for user in progress.bar(all_users):
            # Get categories user follows
            followed_ctgs = user.categories.values('category')
            categories = []
            for i in followed_ctgs:
                categories.append(i['category'])

            # Get circuits with categories of user
            circuits = Circuit.objects.filter(category__in=categories)
            what_circuits = len(circuits)*circuit_percent/100
            # Take only 5% of circuits
            true_circuits = circuits[:what_circuits]
            
            places_ids = []
            for ct in true_circuits:
                places = ct.circuit_stops.values('place')
                for pl in places:
                    places_ids.append(pl['place'])

            # how many places will be marked as done
            tam = len(places_ids)
            mark_done = tam*percentage/100
                        
            all_places = Place.objects.filter(id__in=places_ids)[:mark_done]

            for pl in all_places:
                dp = DonePlace(
                    user = user,
                    place = pl
                )

                dp.save()
                session_counter += 1
                if session_counter > 5000:
                    session_counter = 0
                    transaction.commit()

        transaction.commit()
            
            
