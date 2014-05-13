# -*- coding: utf-8 -*-
import django.dispatch


# shooted on API and view ====================================================
"""
Includes sync methods:
- user_category_follow_add  (Recsys)
"""
category_follow = django.dispatch.Signal(
    providing_args=[
        "category_id"
    ]
)

# shooted on API  ====================================================
"""
Includes sync methods:
- user_category_follow_rmv  (Recsys)
"""
category_unfollow = django.dispatch.Signal(
    providing_args=[
        "category_id"
    ]
)


# shooted on ... ====================================================
"""
Includes sync methods:
-
"""
#user_follow = django.dispatch.Signal(
#    providing_args=[
#        "user_id"
#    ]
#)

# shooted on ... ====================================================
"""
Includes sync methods:
-
"""
#user_unfollow = django.dispatch.Signal(
#    providing_args=[
#        "user_id"
#    ]

