# -*- coding: utf-8 -*-
import redis
from stats.constants import *
from recsys.utils.querying import RedisQuery

class RedisStatsQuery(RedisQuery):
    """
    This class interfaces the querying to the Redis database, automatically
    connects on initialization and must call self.Redis_disconnect once
    you finished using it, has all the methods of the father RedisQuery in case
    you need some querying from CircuitRecsys
    """
    def circuit_fav_count(self, circuit_id):
        """
        Returns a counter of times a circuit has been favorited
        """
        key = ':'.join(
            [CIRCUIT_NMBR_FAVS_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_FAVS_2]
        )
        resp = self.RS.get(key)
        if resp is None:
            return 0
        return resp

    def circuit_favoriting_users(self, circuit_id):
        """
        Returns the set of users that favorited circuit
        """
        key = ':'.join(
            [CIRCUIT_FAV_USRS_1, 
            str(circuit_id), 
            CIRCUIT_FAV_USRS_2]
        )
        return self.RS.smembers(key)

    def circuit_remix_count(self, circuit_id):
        """
        Returns a counter of times a circuit has been favorited
        """
        key = ':'.join(
            [CIRCUIT_NMBR_RMX_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_RMX_2]
        )
        resp = self.RS.get(key)
        if resp is None:
            return 0
        return resp

    def circuit_remixed_circuits(self, circuit_id):
        """
        Returns a set of circuits that are remixed from circuit_id
        """
        key = ':'.join(
            [CIRCUIT_RMX_CTS_1, 
            str(original_id), 
            CIRCUIT_RMX_CTS_2]
        )
        return self.RS.smembers(key)