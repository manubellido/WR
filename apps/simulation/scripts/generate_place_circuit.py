import random
from Distributions.random_distrib import Cumulative_vec_distr
from Distributions.constant_intervals import places_x_circuit
from circuits.models import Circuit, CircuitStop
from places.models import Place
from django.db import transaction
from clint.textui import progress, colored #Eye candy


class Place_circuit_generator(object):
    """
    Populates places in circuits
    """

    @transaction.commit_manually
    def run(self, new_circuits=None):
        if new_circuits == None:
            
            # SELECT id FROM circuits
            all_circuits = Circuit.objects.all()
        else:
            #all_circuits = self.session.query(Circuit).order_by((Circuit.id).desc()).limit(new_circuits).all()
            pass
    
        
        # SELECT id FROM places
        all_places = Place.objects.all()

        # Put places ids on array
        places_ids = []
        for tp in all_places:
            places_ids.append(tp.id)
        
        session_counter = 0
        print colored.white("Populating places for circuits:")
        for ct in progress.bar(all_circuits):

            num_places = Cumulative_vec_distr(places_x_circuit)
            what_places = random.sample(places_ids,num_places)

            for item in xrange(num_places):

                Ct_St = CircuitStop(circuit=ct,
                    place=Place.objects.get(id=what_places[item]),
                    position=1
                )

                Ct_St.save()
                session_counter += 1

                if session_counter >= 5000:            
                    transaction.commit() 
                    session_counter = 0

        transaction.commit()

