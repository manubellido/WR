# -*- coding: utf-8 -*-

import redis
from clint.textui import progress, colored #Eye candy
from recsys.circuits.constants import *
from django.conf import settings


class GenericRecsys(object):
    """
    Generic Recommender system class
    """
    def __init__(self, user):
        """
        @param: user= User instance to recommend to
        """
        self.user = user

    def Set_user(self, other_user):
        """ 
        @param: other_user = new User instance
        """
        self.user = other_user

    def Current_user(self):
        """ Prints on console the current user """
        print colored.white("Current User: "), 
        print colored.white(self.user)

    def Redis_connect(self):
        """ Connects to a Redis server """
        self.RS = redis.StrictRedis(
            host=settings.REDIS.get('HOST', 'localhost'),
            port=settings.REDIS.get('PORT', 6379), 
            db=settings.REDIS.get('DB', 0)
        )
        
    def Redis_disconnect(self):
        """ Disconnects from server """
        self.RS.disconnect()

    def Redis_info(self):
        """ Returns information about the redis server """
        try:
            print colored.white(self.RS.info())
        except AttributeError:
            print colored.red("No connection to server")
        
