import random
from circuits.models import Circuit
from django.db import transaction
from simulation.models import SimUser
from clint.textui import progress, colored #Eye candy

# Dummy classes for mapping
class User(object):
    pass

class CircuitGenerator(object):
    """
    Generates circuits depending on how many circuits
    a user creates as soon as he is created
    """
    
    @transaction.commit_manually
    def run(self, new_users=None):   
     
        if new_users == None:        
            #SELECT id, circuits_to_create FROM users
            #WHERE circuits_to_create > 0;
            all_users = SimUser.objects.filter(circuits_to_create__gt = 0)
        else:
            #all_users = SimUser.objects.order_by((SimUser.id).desc()).limit(new_users)
            pass
    
        cct_name = 'circuit_'
        cct_count = 0
        new_circuits = 0

        session_counter = 0
        print colored.white("Generating circuits:")
        for usuario in progress.bar(all_users):
            for i_circuit in xrange(usuario.circuits_to_create):

                circuit = Circuit(
                    name=cct_name + str(cct_count),
                    author=usuario.user,
                    rating=0,
                    category = random.randint(0,25)
                )    

                cct_count += 1
                session_counter += 1
                circuit.save()
                new_circuits += 1

                if session_counter >= 5000:
                    session_counter = 0
                    transaction.commit()

        transaction.commit()
            
        #return new_circuits


