# -*- coding: utf-8 -*-

import django.dispatch

# shooted on views and API ====================================================
"""
Includes sync methods:
- circuit_count_visit       (Recsys)
- circuit_update_visitor    (Recsys)
"""
circuit_visited = django.dispatch.Signal(
    providing_args=[
        "request"
    ]
)

# shooted on Circuit model ====================================================
"""
Includes sync methods:
- incr_circuit_remix_count  (Stats)
- add_remixed_circuit_id    (Stats)
"""
circuit_remixed = django.dispatch.Signal(
    providing_args=[
        "remixed_circuit_id"
    ]
)

# Shooted on Circuit model  ===================================================
"""
Includes sync methods:
- decr_circuit_remix_count  (Stats)
- rm_remixed_circuit_id     (Stats)
"""
circuit_remix_deleted = django.dispatch.Signal(
    providing_args=[
        "remixed_circuit_id"
    ]
)

# Shooted on API, views use JS with API =======================================
"""
Includes sync methods:
- incr_circuit_fav_count    (Stats)
- add_favoriting_user_id    (Stats)
- user_fav_circuits_add     (Recsys)
"""
circuit_favorited = django.dispatch.Signal(
    providing_args=[
        "user_id"
    ]
)

# Shooted on API, views use JS with API =======================================
"""
Includes sync methods:
- decr_circuit_fav_count    (Stats)
- rm_favoriting_user_id     (Stats)
- user_fav_circuits_rmv     (Recsys)
"""
circuit_unfavorited = django.dispatch.Signal(
    providing_args=[
        "user_id"
    ]
)

# shooted on Circuit model ====================================================
"""
Includes sync methods:
- user_author_circuits_add  (Recsys)
- category_in_circuits_add  (Recsys)
- all_circuits_add          (Recsys)
"""
circuit_created = django.dispatch.Signal()

# shooted on Circuit model ====================================================
"""
Includes sync methods:
- user_author_circuits_rmv  (Recsys)
- category_in_circuits_rmv  (Recsys)
- all_circuits_rmv          (Recsys)
"""
circuit_deleted = django.dispatch.Signal()

# shooted on Circuit model ====================================================
"""
Includes sync methods:
- category_in_circuits_rmv  (Recsys)
"""
circuit_updated = django.dispatch.Signal()

