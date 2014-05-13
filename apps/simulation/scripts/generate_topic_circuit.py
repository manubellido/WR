import random
from Distributions.random_distrib import Cumulative_vec_distr
from Distributions.constant_intervals import topics_x_circuit
from circuits.models import Circuit
from topics.models import Topic
from django.db import transaction
from clint.textui import progress, colored #Eye candy

class Topic_circuit_generator(object):
    """
    Populates the topics in circuits model
    """

    @transaction.commit_manually
    def run(self, new_circuits=None):
        if new_circuits == None:
            # SELECT * FROM circuits
            all_circuits = Circuit.objects.all()
        else:
            #all_circuits = self.session.query(Circuit).order_by((Circuit.id).desc()).limit(new_circuits).all()
            pass

        # SELECT * FROM topics
        all_topics_query = Topic.objects.all()

        # Create an array of topic ids
        all_topics_ids = []
        for tp in all_topics_query:
            all_topics_ids.append(tp.id)
        
        session_counter = 0
        print colored.white("Populating topics for circuit:")
        for circ in progress.bar(all_circuits):
            # Getting how many topics will a circuit have
            num_topics = Cumulative_vec_distr(topics_x_circuit)
            # Getting what topics will this circuit have
            what_topics = random.sample(all_topics_ids, num_topics)

            for topic in xrange(num_topics):
                # Add topic to circuit
                circ.topics.add(what_topics[topic])
                session_counter += 1

                if session_counter >= 5000:
                    session_counter = 0
                    transaction.commit()                
        #Save to db
        transaction.commit()



