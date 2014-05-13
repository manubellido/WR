import redis
from recsys.circuits.constants import *
from recsys.common_recsys import GenericRecsys

# TODO: This entire class should be moved to stats/synchronize.py

class RedisSync(GenericRecsys):
    """
    This class synchronizes the redis structures and is intended to be
    called when a signal to the DB is generated, once instantiated an object 
    of this class, call self.Redis_disconnect() after you finished working
    """
    def __init__(self, user=None):
        if user is not None:
            super(RedisSync, self).__init__(user)
        # The Redis connect will eventually connect to different servers
        # and should get those parameters
        self.Redis_connect()
    
    def user_fav_circuits_add(self, circuit_id, user_id):
        """
        Adds a favorite circuit id to the set of favorites for
        given user
        """
        key = "%s%s%s" % (usr_fav_ct_1, str(user_id), usr_fav_ct_2)
        self.RS.sadd(key, circuit_id)

    def user_fav_circuits_rmv(self, circuit_id, user_id):
        """
        Removes a favorite circuit id to the set of favorites for
        given user
        """
        key = "%s%s%s" % (usr_fav_ct_1, str(user_id), usr_fav_ct_2)
        self.RS.srem(key, circuit_id)
            
    def user_category_follow_add(self, category_value, user_id):
        """
        Adds a category to the following categories for self.user
        """
        key = "%s%s%s" % (usr_ctry_fllw_1, str(user_id), usr_ctry_fllw_2)
        self.RS.sadd(key, category_value)
        
    def user_category_follow_rmv(self, category_value, user_id):
        """
        Removes a category to the following categories for self.user
        """
        key = "%s%s%s" % (usr_ctry_fllw_1, str(user_id), usr_ctry_fllw_2)
        self.RS.srem(key, category_value)
            
    def user_follow_user_add(self, owner_id, user_id):
        """
        Adds a user to the set of followed user for self.user
        """
        key = "%s%s%s" % (usr_usr_fllw_1, str(owner_id), usr_usr_fllw_2)
        self.RS.sadd(key, user_id)
        
    def user_follow_user_rmv(self, owner_id, user_id):
        """
        Removes a user to the set of followed user for self.user
        """
        key = "%s%s%s" % (usr_usr_fllw_1, str(owner_id), usr_usr_fllw_2)
        self.RS.srem(key, user_id)
                   
    def category_in_circuits_add(self, category_value, circuit_id):
        """
        Adds a circuit_id to the set of category
        """
        key = "%s%s%s" % (ctgry_in_cts_1, str(category_value), ctgry_in_cts_2)
        self.RS.sadd(key, circuit_id)
        
    def category_in_circuits_rmv(self, category_value, circuit_id):
        """
        Remoevs a circuit to the set of categories
        """
        key = "%s%s%s" % (ctgry_in_cts_1, str(category_value), ctgry_in_cts_2)
        self.RS.srem(key, circuit_id)
        
    def user_author_circuits_add(self, user_id, circuit_id):
        """
        Adds circuit to the set of circuits where user_id is author
        """
        key = "%s%s%s" % (usr_ct_author_1, str(user_id), usr_ct_author_2)
        self.RS.sadd(key, circuit_id)
        
    def user_author_circuits_rmv(self, user_id, circuit_id):
        """
        Removes circuit to the set of circuits where user_id is author
        """
        key = "%s%s%s" % (usr_ct_author_1, str(user_id), usr_ct_author_2)
        self.RS.srem(key, circuit_id)
       
    def all_circuits_add(self, circuit_id):
        """
        Adds circuit to the set of circuit ids
        """
        key = "%s" % (circuit_ids)
        self.RS.sadd(key, circuit_id)        
        
    def all_circuits_rmv(self, circuit_id):
        """
        Removes circuit to the set of circuit ids
        """
        key = "%s" % (circuit_ids)
        self.RS.srem(key, circuit_id)

    def user_visited_circuits_add(self, user_id, circuit_id):
        """
        Adds a circuit_id to the user set of visited circuits
        """
        key = "%s%s%s" % (usr_ct_visit_1, str(user_id), usr_ct_visit_2)
        self.RS.sadd(key, circuit_id)

    def circuit_count_visit(self, circuit_id):
        """
        Increases the counter of visits associated with a circuit
        """
        key = "%s%s%s" % (ct_visits_1, str(circuit_id), ct_visits_2)
        self.RS.incr(key)

    def circuit_update_visitor(self, circuit_id, user_id, unixtime=None):
        """
        Updates the timestamp of the last visit of circuit by a user
        """
        import time
        if unixtime is None:
            unixtime = time.time()
        key = "%s%s%s" % (circuit_visitors_1, 
            str(circuit_id), 
            circuit_visitors_2
        )
        self.RS.zadd(key, unixtime, user_id)

    def gmac_contains_circuits(self, gmac_id, circuit_id):
        """
        adds circuit_id to the set of circuits that a gmac contains
        """
        key = "%s%s%s" % (gmac_cts_1, str(gmac_id), gmac_cts_2)
        self.RS.sadd(key, circuit_id)
