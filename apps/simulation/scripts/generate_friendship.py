import random
from user_profile.models import UserFollower
from django.contrib.auth.models import User
from Distributions.random_distrib import Cumulative_vec_distr
from Distributions.constant_intervals import friends_x_user
from django.db import transaction
from clint.textui import progress, colored #Eye candy

class FriendshipGenerator(object):
    """ Implements random relationship generation between User objects. """

    @transaction.commit_manually
    def run(self):
        #SELECT * FROM users
        all_users = User.objects.all()
        #users_vec = []
        #for user in all_users:
        #    users_vec.append(user.id)

        session_counter = 0
        print colored.white("Generating Friendships:")
        for user in progress.bar(all_users):
            num_friends = Cumulative_vec_distr(friends_x_user)
            what_friends = random.sample(all_users, num_friends)

            for i in xrange(len(what_friends)):
                # create friendship relation friend
                friend = UserFollower(
                    owner=user,
                    follower=what_friends[i],
                    context=random.randint(1,5)
                )
                
                friend.save()
                session_counter += 1

                if session_counter > 5000:
                    session_counter = 0
                    transaction.commit()

        transaction.commit()
                    

