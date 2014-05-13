import redis
from recsys.circuits.constants import *
from recsys.common_recsys import GenericRecsys

class RedisQuery(GenericRecsys):
    """
    This class interfaces the querying to the Redis database, automatically
    connects on initialization and must call self.Redis_disconnect once
    you finished using it
    """
    def __init__(self, user=None):
        if user is not None:
            super(RedisQuery, self).__init__(user)
        # The Redis connect will eventually connect to different servers
        # and should get those parameters
        self.Redis_connect()
        
    def user_fav_circuits(self, user_id=None):
        """
        Returns a set containing the ids of circuits that user has as favorites
        """
        if user_id is None:
            key = "%s %s %s" % (usr_fav_ct_1, str(self.user), usr_fav_ct_2)
            return self.RS.smembers(key)
            
        key = "%s %s %s" % (usr_fav_ct_1, str(user_id), usr_fav_ct_2)
        return self.RS.smembers(key)
        
        
    def user_is_favorite(self, circuit_id, user_id=None):
        """
        Returns a boolean indicating if circuit is favorited by user
        """
        if user_id is None:
            key = "%s %s %s" % (usr_fav_ct_1, str(self.user), usr_fav_ct_2)
            return self.RS.sismember(key, circuit_id)
            
        key = "%s %s %s" % (usr_fav_ct_1, str(user_id), usr_fav_ct_2)
        return self.RS.sismember(key, circuit_id)
        
    def user_category_follow(self, user_id=None):
        """
        Returns a set containing all the categories followed by user
        """
        if user_id is None:
            key = "%s %s %s" % (usr_ctry_fllw_1, 
                str(self.user), 
                usr_ctry_fllw_2
            )
            return self.RS.smembers(key)
            
        key = "%s %s %s" % (usr_ctry_fllw_1, str(user_id), usr_ctry_fllw_2)
        return self.RS.smembers(key)
        
    def user_follow_category(self, category_id, user_id=None):
        """
        Returns a boolean indicating if category_id is followed by user
        """
        if user_id is None:
            key = "%s %s %s" % (usr_ctry_fllw_1, 
                str(self.user), 
                usr_ctry_fllw_2
            )
            return self.RS.sismember(key, category_id)
            
        key = "%s %s %s" % (usr_ctry_fllw_1, str(user_id), usr_ctry_fllw_2)
        return self.RS.sismember(key, category_id)
        
    def user_follow_users(self, user_id=None):
        """
        Returns a set containing all the users followed by user
        """
        if user_id is None:
            key = "%s %s %s" % (usr_usr_fllw_1, str(self.user), usr_usr_fllw_2)
            return self.RS.smembers(key)
            
        key = "%s %s %s" % (usr_usr_fllw_1, str(user_id), usr_usr_fllw_2)
        return self.RS.smembers(key)
        
    def user_does_follow_user(self, fuser_id, user_id=None):
        """
        Returns a boolean indicating if fuser is currently being
        followed by user
        """
        if user_id is None:
            key = "%s %s %s" % (usr_usr_fllw_1, str(self.user), usr_usr_fllw_2)
            return self.RS.sismember(key, fuser_id)
            
        key = "%s %s %s" % (usr_usr_fllw_1, str(user_id), usr_usr_fllw_1)
        return self.RS.sismember(key, fuser_id)

    def circuit_visits(self, circuit_id):
        """
        Returns the number of visits that a circuit has
        """
        key = "%s %s %s" % (ct_visits_1, str(circuit_id), ct_visits_2)
        resp = self.RS.get(key)
        if resp is None:
            return 0
        return resp
        
    def category_in_circuits(self, category_id):
        """
        Returns a set of circuits, every of these circuits has category_id
        as the category they belong to
        """
        key = "%s %s %s" % (ctgry_in_cts_1, str(category_id), ctgry_in_cts_2)
        return self.RS.smembers(key)
        
    def circuit_has_category(self, circuit_id, category_id):
        """
        Returns a boolean indicating if circuit has category_id as category
        """
        key = "%s %s %s" % (ctgry_in_cts_1, str(category_id), ctgry_in_cts_2)
        return self.RS.sismember(key, circuit_id)

    def user_visited_circuits(self, user_id=None):
        """
        Returns a set of visited circuits by user
        """
        if user_id is None:
            key = "%s %s %s" % (usr_ct_visit_1, 
                str(self.user), 
                usr_ct_visit_2
            )
            return self.RS.smembers(key)
            
        key = "%s %s %s" % (usr_ct_visit_1, str(user_id), usr_ct_visit_2)
        return self.RS.smembers(key)
        
    def user_author_cricuits(self, user_id=None):
        """
        Returns a set containing all circuits that has user as author
        """
        if user_id is None:
            key = "%s %s %s" % (usr_ct_author_1, 
                str(self.user), 
                usr_ct_author_2
            )
            return self.RS.smembers(key)
            
        key = "%s %s %s" % (usr_ct_author_1, str(user_id), usr_ct_author_2)
        return self.RS.smembers(key)
        
    def user_is_author(self, circuit_id, user_id=None):
        """
        Returns a boolean indicating if user is author of circuit
        """
        if user_id is None:
            key = "%s %s %s" % (usr_ct_author_1, 
                str(self.user), 
                usr_ct_author_2
            )
            return self.RS.sismember(key, fuser_id)
            
        key = "%s %s %s" % (usr_ct_author_1, str(user_id), usr_ct_author_2)
        return self.RS.sismember(key, fuser_id)
        
    def all_circuits(self):
        """
        Returns a set of circuits_ids for all the existant circuits
        """
        key = "%s" % (circuit_ids)
        return self.RS.smembers(key)
        
    def circuit_exists(self, circuit_id):
        """
        Returns a boolean indicating of circuit exists
        """
        key = "%s" % (circuit_ids)
        return self.RS.sismember(key, circuit_id)
        
        
