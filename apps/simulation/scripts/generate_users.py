import random
from Distributions.random_distrib import Cumulative_vec_distr
from Distributions.constant_intervals import circuits_x_user, score_prob
from django.contrib.auth.models import User
from django.db import transaction
from simulation.models import SimUser
from clint.textui import progress, colored #Eye candy

class UserGenerator(object):
    """
    Generates user randomly from names.txt
    """

    #By default, there should be a 'names.txt' file in the same folder
    def __init__(self):
        self.names_file = "names.txt"

    @transaction.commit_manually
    def run(self):
        try:
            # File containing 10 000 user names obtained from Twitter
            names = open(self.names_file, 'r').readlines()

        except IOError, e:
            print e

        print colored.white("Generating users:")
        for name in progress.bar(names):
            # Create ...auth.models.User
            new_user = User(username=name)
            # Save to db
            new_user.save()

            # Create models.SimUser
            sim_user = SimUser(
                user=new_user,
                free_time_score=Cumulative_vec_distr(score_prob),
                explorer_score=Cumulative_vec_distr(score_prob), 
                pop_score=Cumulative_vec_distr(score_prob), 
                circuits_to_create = Cumulative_vec_distr(circuits_x_user))

            # Save to db
            sim_user.save()
        transaction.commit()

    # TODO
    def simulate(self, new_usrs=10):
        """
        Simulates the creation of new users
        
        print colored.white("Simulating users")
        for i in progress.bar(xrange(new_usrs)):
            new_user = User(
                    screen_name='',
                    free_time_score=Cumulative_vec_distr(score_prob),
                    explorer_score=Cumulative_vec_distr(score_prob), 
                    pop_score=Cumulative_vec_distr(score_prob), 
                    circuits_to_create = Cumulative_vec_distr(circuits_x_user))
            
            self.session.add(user)
        return new_usrs
        """






