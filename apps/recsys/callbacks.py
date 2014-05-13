# -*- coding: utf-8 -*-
import uuid

from user_profile.signals import category_follow, category_unfollow
from recsys.utils.synchronize import RedisSync

def process_category_follow(sender, **kwargs):
    # grab user
    user = sender
    # get category_id
    category_id = kwargs.get('category_id', None)
    if category_id is None:
        return
    R = RedisSync()
    # sync to Redis
    R.user_category_follow_add(category_value=category_id, user_id=user.pk)

def process_category_unfollow(sender, **kwargs):
    # grab user
    user = sender
    # get category_id
    category_id = kwargs.get('category_id', None)
    if category_id is None:
        return
    R = RedisSync()
    # sync to Redis
    R.user_category_follow_rmv(category_value=category_id, user_id=user.pk)


# Conecting signals ===========================================================
category_follow.connect(
    process_category_follow, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)

category_unfollow.connect(
    process_category_unfollow, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)