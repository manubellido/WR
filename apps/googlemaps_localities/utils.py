# -*- coding: utf-8 -*-

import redis
from django.conf import settings

def get_redis_connection():
    return redis.StrictRedis(
        host=settings.REDIS.get('HOST', 'localhost'),
        port=settings.REDIS.get('PORT', 6379), 
        db=settings.REDIS.get('DB', 0)
    )
