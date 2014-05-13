# -*- coding: utf-8 -*-
import redis

from clint.textui import progress, colored #Eye candy
from recsys.common_recsys import GenericRecsys
from recsys.circuits.constants import *
from recsys.utils.querying import RedisQuery

from googlemaps_localities.models import GoogleMapsAddressComponent as GMAC
from circuits.models import Circuit

class CircuitRecsys(GenericRecsys):
    """
    Circuit recommender system
    """
    def __init__(self, user):
        """
        @param: user= User id to recommend to
        """
        super(CircuitRecsys, self).__init__(user)
        # variable for knowing if recommending geographically
        self.has_gmac = False
        self.gmac = None

    def Print_scores(self):
        """ Prints in console every circuit_id -> value """
        for key, value in self.scores.items():
            print colored.yellow(key), 
            print colored.cyan("\t==>\t"), 
            print colored.magenta(value)

    def Get_self_scores_key(self):
        """ Returns the key for self sorted set that sorts recommended circuits
            locally """
        return "%s:%s:%s" % ('usr', str(self.user), 'recomm')

    def Set_gmac(self, gmac_id):
        """
        first filtered circuits should be filtered by gmac, for filtering
        recommendations by location
        """
        try:
            self.gmac = GMAC.objects.get(pk=gmac_id)
            self.has_gmac = True
        except GMAC.DoesNotExist:
            return

    def Redis_recomm(self):
        """ 
        Creates on Redis a sorted set with the final recommendation for user,
        key is usr:[usr_id]:recomm, sorted by score
        """
        this_key = self.Get_self_scores_key()
        for key, value in self.scores.items():
            self.RS.zadd(this_key, int(value), key)

    def Recomm_top_n(self, top_n):
        """ 
        Returns the ids of the top 5 circuits to recommend to the user
        """
        this_key = self.Get_self_scores_key()
        recommended = self.RS.zrange(this_key, 0, top_n, desc=True)
        return recommended
        
    def Give_me_the_fun(self, top_n=10):
        """ Run the point based recommended system
        """
        self.scores = {}
        self.Redis_connect()
        self.Filter_circuits()
        self.Point_category_follow(3)
        #self.Point_topic_follow(5)
        #self.Point_author_follow(4)
        self.Point_follow_upvote(2)
        #self.Point_friend_visited(1)
        self.Point_circuit_rating(1)
        #self.Print_scores()
        self.Redis_recomm()
        return self.Recomm_top_n(top_n)
        
    def Filter_circuits(self):
        """
        Returns a dictionary with all the circuits that are able
        to be recommended to user
        """
        R = RedisQuery(self.user)
        #Get circuits ids user has visited
        #vis_cts_ids = R.user_visited_circuits()
    
        # Get possibly recommended circuits
        if self.has_gmac:
            # TODO: @mathiasbc , improve with Redis dont query to DB
            all_gmacs_ids = GMAC.get_id_list_from_redis(self.gmac.pk)
            all_gmacs = GMAC.objects.filter(pk__in=all_gmacs_ids)
            circuits = Circuit.filter_by_gmacs(all_gmacs)
            all_circuits = []
            for ct in circuits:
                if ct.pk not in all_circuits:
                    all_circuits.append(ct.pk)
        else:
            all_circuits = R.all_circuits()
        
        # Initiate scores dict with posible recommendation circuits
        for i in all_circuits:
            #if i not in vis_cts_ids:
            self.scores[i] = 0

    def Scores_update(self, circuits, points):
        """
        Updates the values of scores dictionary depending on
        the ids in the set circuits, adds + points
        """
        for ct in circuits:
            if self.scores.has_key(ct):
                self.scores[ct] += points

    def Point_category_follow(self, points):
        """
        Returns the dictionary scores with value increased
        for circuits that has category the user follows
        """
        R = RedisQuery(self.user)
        # Get categories user follows
        followed_ctgs = R.user_category_follow()

        circuits = []
        # Get circuits that has followed categories
        for ctry in followed_ctgs:
            cts = R.category_in_circuits(ctry)
            for ct in cts:
                circuits.append(ct)
        
        # increase scores for circuits
        self.Scores_update(circuits, points)

    def Point_topic_follow(self, points):
        """
        Returns the dictionary scores with value increased
        for circuits that has topics that the user follows
        """
        # Get topics the user follows
        this_key = usr_tp_fllw_1 + str(self.user) + usr_tp_fllw_2
        followed_tps = self.RS.smembers(this_key)        

        circuits = []
        # Get circuits that has followed topics
        for tp in followed_tps:
            this_key = topic_in_cts_1 + tp + topic_in_cts_2
            cts = self.RS.smembers(this_key)
            for ct in cts:
                circuits.append(ct)
    
        # Increment circuits scores
        self.Scores_update(circuits, points)

    def Point_author_follow(self, points):
        """
        Increases the score of circuit whos author is
        beeing followed by user
        """
        # Get the users that user follows
        this_key = usr_usr_fllw_1 + str(self.user) + usr_usr_fllw_2
        followed_users = self.RS.smembers(this_key)

        circuits = []
        # Circuits with author beeing followed by user
        for usr in followed_users:
            this_key = usr_ct_author_1 + usr + usr_ct_author_2
            cts = self.RS.smembers(this_key)
            for ct in cts:
                circuits.append(ct)
    
        # increse score for circuits
        self.Scores_update(circuits, points)

    def Point_follow_upvote(self, points):
        """
        Increases the score of circuits that were upvoted
        by users that user follows
        """
        # Get the users that user follows
        this_key = usr_usr_fllw_1 + str(self.user) + usr_usr_fllw_2
        followed_users = self.RS.smembers(this_key)

        circuits = []
        # Get the upvoted circuits of followed users
        for usr in followed_users:
            this_key = usr_ct_upvt_1 + usr + usr_ct_upvt_2
            cts = self.RS.smembers(this_key)
            for ct in cts:
                circuits.append(ct)
    
        # increse score for circuits
        self.Scores_update(circuits, points)

    def Point_friend_visited(self, points):
        """
        Increases the score of circuits that were visited
        by friends
        """
        # Get the users that user follows
        this_key = usr_usr_fllw_1 + str(self.user) + usr_usr_fllw_2
        followed_users = self.RS.smembers(this_key)

        circuits = []
        # Get the visited circuits of followed users
        for usr in followed_users:
            this_key = usr_ct_visit_1 + usr + usr_ct_visit_2
            cts = self.RS.smembers(this_key)
            for ct in cts:
                circuits.append(ct)
    
        # increse score for circuits
        self.Scores_update(circuits, points)

    def Point_circuit_rating(self, points):
        """
        Increases score of circuits that has an approval of
        more than 70%
        """
        for key, value in self.scores.items():
            # Get circuit upvotes
            upvotes = self.RS.get(ct_votes + str(key) + ct_vote_up)
            if upvotes is None:
                up = 0
            else:
                up = int(self.RS.get(ct_votes + str(key) + ct_vote_up))

            # Get circuit downvotes
            downvotes = self.RS.get(ct_votes + str(key) + ct_vote_dwn)
            if downvotes is None:
                dwn = 0
            else:
                dwn = int(self.RS.get(ct_votes + str(key) + ct_vote_dwn))

            if up+dwn == 0:
                return

            rating = (up * 100)/(up + dwn)
            if rating >= 70:
                self.scores[key] += points
            

