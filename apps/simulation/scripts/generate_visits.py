import random
from circuits.models import Circuit
from visits.models import Visit
from simulation.models import SimUser
from django.db import transaction
from Distributions.constant_intervals import hour_x_day_accum, visit_duration_accum
from Distributions.random_distrib import Cumulative_vec_samples, Cumulative_vec_distr
from datetime import datetime, timedelta
from clint.textui import progress, colored #Eye candy

class VisitGenerator(object):
    """
    Simulates the initial data for users visiting some circuits
    """

    def __init__(self, date=None):
        if date == None:
            date = datetime.today()
        self.date = date

    @transaction.commit_manually
    def run(self, min_equiv=360):
        """
        @param: min_equiv = how many minutes correspond to a 100 free_time_score
        """
        min_equiv /= 100 

        
        # SELECT screen_name, free_time_score FROM users
        # ORDER BY free_time_score DESC;
        all_users = SimUser.objects.order_by('-free_time_score')
        
        # SELECT circuit.id FROM circuits
        all_circuits = Circuit.objects.all()
        circuits_size = len(all_circuits)
    
        session_counter = 0
        print colored.white("Inserting visits for user:")
        for usuario in progress.bar(all_users):
            #Probability that a user does not visit this day ~50%
            skip_visit = random.randint(0,30)
            if skip_visit > 15:
                continue
            
            # Calculating users available time
            watch_time = usuario.free_time_score * min_equiv
            factor = int(0.3 * watch_time)
            total_time = random.randint(-factor,factor) + watch_time

            # Get user visit begin time in 24hrs format
            begin_hour = Cumulative_vec_samples(hour_x_day_accum,1)
            # Create a timestamp
            #timestamp = datetime(self.date.year,
            #                     self.date.month,
            #                     self.date.day,
            #                     begin_hour[0],
            #                     0, 0)

            while total_time > 0:
                # Getting the duration in minutes of the visit
                visit_duration = Cumulative_vec_distr(visit_duration_accum)
                
                # Creating an instance of visit
                visita = Visit(
                            visitor = usuario.user,
                            # visit random circuit, cause could visit the same circuit twice or more
                            content_object = all_circuits[random.randint(1,circuits_size-1)]
                )

                # Adding visit minutes to timestamp
                #timestamp += timedelta(minutes=visit_duration)    
                # Save visit to DB
                visita.save()
                # updating total_time
                total_time -= visit_duration

                session_counter += 1
                if session_counter >= 5000:
                    session_counter = 0
                    transaction.commit()

        transaction.commit()


