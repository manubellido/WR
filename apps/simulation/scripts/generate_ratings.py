import random
from django.db import transaction
#from simulation.models import SimUser
from circuits.models import Circuit, CircuitRating
from clint.textui import progress, colored #Eye candy

class RatingsGenerator(object):
    """Random rating relationships between User and Circuit """

    @transaction.commit_manually
    def run(self):
        """ 80% pending vote, 17% up vote, y 3% down vote """
        
        # SELECT circuit.id FROM circuits
        all_circuits = Circuit.objects.all()

        session_counter = 0
        print colored.white("Inserting ratings for circuit:")
        for ct in progress.bar(all_circuits):
            
            ct_visitors = ct.get_visitors()
            for visitor in ct_visitors:
                prob_vote = random.randint(0,100)
                
                if prob_vote <= 80:
                    continue
                elif prob_vote > 80 and prob_vote <= 93:
                    voto = 1
                else:
                    voto = -1

                ct_r = CircuitRating(user=visitor,
                    circuit=ct,
                    vote = voto
                )   

                ct_r.save()
                session_counter += 1
                if session_counter >= 5000:
                    session_counter = 0
                    transaction.commit()

        transaction.commit()
                
