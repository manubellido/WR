from Distributions.random_distrib import Cumulative_vec_distr
from Distributions.constant_intervals import categories_x_user, choose_categorie_h, choose_categorie_m
from circuits.models import CircuitCategoryFollow
from django.contrib.auth.models import User
from simulation.models import SimUser
from django.db import transaction
from clint.textui import progress, colored #Eye candy

class CategoryFollowGenerator(object):
    """
    Generates simulation for the categories a User is going to follow
    """

    @transaction.commit_manually
    def run(self):
        all_users = SimUser.objects.all()
        
        session_counter = 0
        print colored.white("Generating user category follow:")
        for usr in progress.bar(all_users):
            how_many_categories = Cumulative_vec_distr(categories_x_user)

            what_categories = []
            if usr.gender == 1 or usr.gender == 3:
                for i in xrange(how_many_categories):
                    cgry = Cumulative_vec_distr(choose_categorie_h)    
                    while cgry in what_categories:
                        cgry = Cumulative_vec_distr(choose_categorie_h)

                    what_categories.append(cgry)
            else:
                for i in xrange(how_many_categories):
                    cgry = Cumulative_vec_distr(choose_categorie_m)    
                    while cgry in what_categories:
                        cgry = Cumulative_vec_distr(choose_categorie_m)

                    what_categories.append(cgry)

            for i in xrange(len(what_categories)):
                ct_fl = CircuitCategoryFollow(
                    user= usr.user,
                    category=what_categories[i] 
                )

                ct_fl.save()
                session_counter += 1

                if session_counter > 5000:
                    session_counter = 0
                    transaction.commit()

        transaction.commit()

            
        
