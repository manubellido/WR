import random
from django.db import transaction
from topics.models import Topic
from clint.textui import progress, colored #Eye candy

class TopicGenerator(object):
    """Generating random topics"""

    def __init__(self, amount=200):
        self.amount = amount

    @transaction.commit_manually
    def run(self):
        chunks = {}

        chunks['bottom'] = (self.amount * 60) / 100
        chunks['middle'] = (self.amount * 30) / 100
        chunks['top'] = self.amount - (chunks['bottom'] + chunks['middle'])

        bottom_vals = [random.randint(1, 80) for i in range(chunks['bottom'])]
        bottom = []

        print colored.white("Generating topics level 0:")
        for elem in progress.bar(bottom_vals):
            new_topic = Topic()
            bottom.append(new_topic)
            
            new_topic.save()
        middle = []
        transaction.commit()

        print colored.white("Generating topics level 1:")
        for i in progress.bar(range(chunks['middle'])):
            children = random.sample(bottom, random.randint(8, 11))

            new_topic = Topic()
            new_topic.save()

            for child in children:
                new_topic.parent.add(child)

            middle.append(new_topic)
        
        print colored.white("Generating topics level 2:")
        for i in progress.bar(range(chunks['top'])):
            children = random.sample(middle, random.randint(4, 7))

            new_topic = Topic()
            new_topic.save()

            for child in children:
                new_topic.parent.add(child)

        transaction.commit()
