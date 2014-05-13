import random
from topics.models import ExplicitInterest
from simulation.models import SimUser
from topics.models import Topic
from django.db import transaction
from datetime import datetime
from clint.textui import progress, colored #Eye candy

class ExplicitGenerator(object):
    """
    Populates the table 'explicit_interest' indicating a user
    saying he likes a topic
    """
    def __init__(self, date=None):
        if date is None:
            self.date = datetime.today()
        else:
            self.date = date

    @transaction.commit_manually
    def run(self):
        # SELECT * FROM users
        # ORDER BY explorer_score DESC LIMIT 2000;
        all_users = SimUser.objects.order_by('-explorer_score')[:2000]
        
        #SELECT topic.id FROM topics
        all_topics = Topic.objects.all()
    
        # Create array of the ids of Topics
        topics_ids = []
        for item in all_topics:
            topics_ids.append(item.id)
    
        session_counter = 0
        print colored.white("Generating explicit interest for user:")
        for usuario in progress.bar(all_users):
            # Number of interests for user
            num_interests = usuario.explorer_score/20
            what_follow = random.sample(topics_ids, num_interests)            
    
            for elem in xrange(num_interests):
                # Get topic from DB
                hole_topic = Topic.objects.get(id=what_follow[elem])
                # Create Interest
                expl = ExplicitInterest(date=self.date,
                                    user=usuario.user,
                                    topic=hole_topic)

                session_counter += 1
                expl.save()
                if session_counter >= 5000:
                    session_counter = 0
                    transaction.commit()

        # Save to DB
        transaction.commit()
        
