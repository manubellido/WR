import random
from datetime import datetime
from topics.models import TopicFollow, Topic
from django.db import transaction
from simulation.models import SimUser
from circuits.models import Circuit
from visits.models import Visit
from clint.textui import progress, colored #Eye candy

class FollowGenerator(object):
    """
    Populates the table 'follows' for simulation
    10% of users use a follow feature
    """
    def __init__(self, date=None):
        if date == None:
            date = datetime.today()
        self.date = date

    @transaction.commit_manually
    def run(self, new_users=None):

        if new_users == None:
            #SELECT screen_name, (free_time_score + explorer_score)/4
            #FROM users
            #ORDER BY (free_time_score + explorer_score) DESC LIMIT 1000;
            all_users = SimUser.objects.order_by('-explorer_score')[:1000]
        else:
            #all_users = self.session.query(User).order_by((User.id).desc()).limit(new_users).all()
            pass

        session_counter = 0
        print colored.white("Generating follows:")
        for usuario in progress.bar(all_users):

            #SELECT DISTINCT(tc.topic_id)
            #FROM visits as v, topic_circuit as tc 
            #WHERE v.circuit_id = tc.circuit_id and v.user_id = all_users.id;
            vis = usuario.user.visits.values('circuit')
            user_visited_cts_ids = []
            for elem in vis:
                user_visited_cts_ids.append(elem['circuit'])

            all_user_topics = []
            for ct in user_visited_cts_ids:
                cir = Circuit.objects.get(id=ct)
                all_user_topics = cir.topics.values('id')
            
            all_user_tpc_ids = []
            for tp in all_user_topics:
                all_user_tpc_ids.append(tp['id'])
            
            # Obtaining how many follows the user will do
            num_follows = (usuario.free_time_score + usuario.explorer_score)/4
            
            while num_follows > len(all_user_topics):
                num_follows -= 1

            # User will follow this topics     
            topics_to_follow = random.sample(all_user_tpc_ids, num_follows)

            for fw in xrange(num_follows):
                # Get the topic from DB
                the_topic = Topic.objects.get(id=topics_to_follow[fw])
                # Create the object Follow
                follow = TopicFollow(date = self.date,
                    user = usuario.user,
                    topic = the_topic
                )

                # Save to DB
                follow.save()
                session_counter += 1

                if session_counter >= 5000:            
                    transaction.commit() 
                    session_counter = 0

        transaction.commit()
            
