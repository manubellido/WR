# -*- coding: utf-8 -*-
import redis

from stats.constants import *
from recsys.utils.synchronize import RedisSync

class RedisStatsSync(RedisSync):
    """
    This class synchronizes the redis structures and is intended to be
    called when a signal to the DB is generated, once instantiated an object 
    of this class, call self.Redis_disconnect() after you finished working,
    has methods of Father for synchronizing user_favorite_circuits for example
    """
    def incr_circuit_fav_count(self, circuit_id):
        """
        Increases the counter of times a circuit has been favorited
        """
        key = ':'.join(
            [CIRCUIT_NMBR_FAVS_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_FAVS_2]
        )        
        self.RS.incr(key)

    def decr_circuit_fav_count(self, circuit_id):
        """
        Decreases the counter of times a circuit has been favorited
        """
        key = ':'.join(
            [CIRCUIT_NMBR_FAVS_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_FAVS_2]
        )
        if self.RS.get(key) < 0:
            self.RS.set(key,1)
        self.RS.decr(key)

    def set_circuit_fav_count(self, circuit_id, number):
        """
        sets the counter of circuit favorites to number
        """
        key = ':'.join(
            [CIRCUIT_NMBR_FAVS_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_FAVS_2]
        )        
        self.RS.set(key, number)

    def add_favoriting_user_id(self, circuit_id, user_id):
        """
        Add a user id to the circuit's set of favoriting users.
        """
        key = ':'.join(
            [CIRCUIT_FAV_USRS_1, 
            str(circuit_id), 
            CIRCUIT_FAV_USRS_2]
        )
        self.RS.sadd(key, user_id)

    def rm_favoriting_user_id(self, circuit_id, user_id):
        """
        Remove a user id from the circuit's set of favoriting users.
        """
        key = ':'.join(
            [CIRCUIT_FAV_USRS_1, 
            str(circuit_id), 
            CIRCUIT_FAV_USRS_2]
        )
        self.RS.srem(key, user_id)

    def incr_circuit_remix_count(self, circuit_id):
        """
        Increases the counter of times a circuit has been remixed
        """
        key = ':'.join(
            [CIRCUIT_NMBR_RMX_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_RMX_2]
        )
        self.RS.incr(key)

    def decr_circuit_remix_count(self, circuit_id):
        """
        Decreases the counter of times a circuit has been remixed
        """
        key = ':'.join(
            [CIRCUIT_NMBR_RMX_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_RMX_2]
        )
        if self.RS.get(key) < 0:
            self.RS.set(key,1)
        self.RS.decr(key)

    def set_circuit_remix_count(self, circuit_id, number):
        """
        sets the counter of times a circuit has been remixed
        """
        key = ':'.join(
            [CIRCUIT_NMBR_RMX_1, 
            str(circuit_id), 
            CIRCUIT_NMBR_RMX_2]
        )
        self.RS.set(key, number)

    def add_remixed_circuit_id(self, original_id, remixed_id):
        """
        Add a remixed circuit id to the original circuit's set of remixed
        circuits.
        """
        key = ':'.join(
            [CIRCUIT_RMX_CTS_1, 
            str(original_id), 
            CIRCUIT_RMX_CTS_2]
        )
        self.RS.sadd(key, remixed_id)

    def rm_remixed_circuit_id(self, original_id, remixed_id):
        """
        Remove a remixed circuit id from the original circuit's set of
        remixed circuits.
        """
        key = ':'.join(
            [CIRCUIT_RMX_CTS_1, 
            str(original_id), 
            CIRCUIT_RMX_CTS_2]
        )
        self.RS.srem(key, remixed_id)
