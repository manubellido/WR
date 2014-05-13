# -*- coding: utf-8 -*-

"""
Constants keys on Redis for Circuit Recsys
"""


# TODO: all of these constants should be moved to the stats app
# Also, there's plenty of repeated values here

# Definition: user visited circuits
# type: set
# key = usr:[usr_id]:ct_visit 
usr_ct_visit_1 = 'usr:'
usr_ct_visit_2 = ':ct_visit'

# Definition: users that have visited a circuit
# type: sorted set
# key = circuit:[circuit_id]:visitors
circuit_visitors_1 = 'circuit:'
circuit_visitors_2 = ':visitors'

# Definition: user favorite circuits
# type: set
# key = usr:[usr_id]:fav_cts 
usr_fav_ct_1 = 'usr:'
usr_fav_ct_2 = ':fav_cts'

# Definition: all circuit ids
# type: set
# key = circuits:ids
circuit_ids = 'circuits:ids'

# Definition: categories that a user follows
# type: set
# key = usr:[usr_id]:ctry_fllw
usr_ctry_fllw_1 = 'usr:'
usr_ctry_fllw_2 = ':ctry_fllw'

# Definition: circuits that contain the given category
# type: set
# key = ctgry:[ctgry_id]:in_cts
ctgry_in_cts_1 = 'ctgry:'
ctgry_in_cts_2 = ':in_cts'

# Definition: topics followed by user
# type: set
# key = usr:[usr_id]:tp_fllw
usr_tp_fllw_1 = 'usr:'
usr_tp_fllw_2 = ':tp_fllw'

# Definition: circuits that contain the given topic
# type: set
# key = topic:[tp_id]:in_cts
topic_in_cts_1 = 'topic:'
topic_in_cts_2 = ':in_cts'

# Definition: user friendships, follow relation
# type: set
# key = usr:[user_id]:usr_fllw
usr_usr_fllw_1 = 'usr:'
usr_usr_fllw_2 = ':usr_fllw'

# Definition: user author of circuits
# type: set
# key = usr:[usr_id]:ct_author
usr_ct_author_1 = 'usr:'
usr_ct_author_2 = ':ct_author'

# Definition: user upvoted circuits
# type: set
# key = usr:[usr_id]:ct_upvt
usr_ct_upvt_1 = 'usr:'
usr_ct_upvt_2 = ':ct_upvt'

# Definition: upvotes and downvotes per circuit
# type: counter
# key = ct:[ct_id]:upvotes
#     = ct:[ct_id]:dwnvotes
ct_votes = 'ct:'
ct_vote_up = ':upvotes'
ct_vote_dwn = ':dwnvotes'

# Definition: Raw number of visits per circuit
# type: counter
# key = ct:[ct_id]:visits
ct_visits_1 = 'ct:'
ct_visits_2 = ':visits'

# Definition: ids of circuits per GMAC, includes all sons
# type: set
# key = gmac:[gmac_id]:cts
gmac_cts_1 = 'gmac:'
gmac_cts_2 = ':cts'












