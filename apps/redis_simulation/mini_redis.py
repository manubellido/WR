# -*- coding: utf-8 -*-

import random
import redis

# Set constants
num_circuits = 30
num_users = 50
num_topics = 12
num_categories = 7

# Set connection to Redis Server
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Definition: all circuit ids
# type: set
# key = circuits:ids
for i in xrange(num_circuits):
    r.sadd('circuits:ids', i)

# Definition: comments on circuit
# type: sorted set
# key = ct:comments
for i in xrange(num_circuits):
    #       key-name    member  score
    r.zadd('ct:comments', i, random.randint(1,10))


# Definition: visits on circuits
# type: sorted set
# key = ct:visits
for i in xrange(num_circuits):
    r.zadd('ct:visits', i, random.randint(5,30))


# Definition: user friendships, follow relation
# type: set
# key = usr:[user_id]:usr_fllw
key_part1 = 'usr:'
key_part2 = ':usr_fllw'
for i in xrange(num_users):
    key = key_part1 + str(i) + key_part2
    how_many_friends = random.randint(4,15)
    
    for friend in xrange(how_many_friends):
        r.sadd(key, random.randint(0, num_users-1))


# Definition: upvotes and downvotes per circuit
# type: counter
# key = ct:[ct_id]:upvotes
#     = ct:[ct_id]:dwnvotes
key_part1 = 'ct:'
key_part2_up = ':upvotes'
key_part2_dwn = ':dwnvotes'
for i in xrange(num_circuits):
    up_key = key_part1 + str(i) + key_part2_up
    dwn_key = key_part1 + str(i) + key_part2_dwn
    
    r.set(up_key, random.randint(0,10))
    r.set(dwn_key, random.randint(0,6))


# Definition: user visited circuits
# type: set
# key = usr:[usr_id]:ct_visit 
key_part1 = 'usr:'
key_part2 = ':ct_visit'
for i in xrange(num_users):
    key = key_part1 + str(i) + key_part2
    how_many_cts = random.randint(6,30)
    
    for vt in xrange(how_many_cts):
        r.sadd(key, random.randint(0, num_circuits-1))


# Definition: topics followed by user
# type: set
# key = usr:[usr_id]:tp_fllw
key_part1 = 'usr:'
key_part2 = ':tp_fllw'
for i in xrange(num_users):
    key = key_part1 + str(i) + key_part2
    how_many_tps = random.randint(1,6)

    for tp in xrange(how_many_tps):
        r.sadd(key, random.randint(0, num_topics-1))


# Definition: circuits that contain the given topic
# type: set
# key = topic:[tp_id]:in_cts
key_part1 = 'topic:'
key_part2 = ':in_cts'
for i in xrange(num_topics):
    key = key_part1 + str(i) + key_part2
    how_many_cts = random.randint(2, 8)
    
    for ct in xrange(how_many_cts):
        r.sadd(key, random.randint(0, num_circuits-1))


# Definition: categories that a user follows
# type: set
# key = usr:[usr_id]:ctry_fllw
key_part1 = 'usr:'
key_part2 = ':ctry_fllw'
for i in xrange(num_users):
    key = key_part1 + str(i) + key_part2
    how_many_ctrys = random.randint(1, 5)
    
    for ctry in xrange(how_many_ctrys):
        r.sadd(key, random.randint(0, num_categories-1))


# Definition: circuits that contain the given category
# type: set
# key = ctgry:[ctgry_id]:in_cts
key_part1 = 'ctgry:'
key_part2 = ':in_cts'
for i in xrange(num_categories):
    key = key_part1 + str(i) + key_part2
    how_many_cts = random.randint(4, 12)
    
    for ct in xrange(how_many_cts):
        r.sadd(key, random.randint(0, num_circuits-1))


# Definition: user author of circuits
# type: set
# key = usr:[usr_id]:ct_author
key_part1 = 'usr:'
key_part2 = ':ct_author'
for i in xrange(num_users):
    key = key_part1 + str(i) + key_part2
    how_many_cts = random.randint(0, 4)
    
    for ct in xrange(how_many_cts):
        r.sadd(key, random.randint(0, num_circuits-1))


# Definition: user upvoted circuits
# type: set
# key = usr:[usr_id]:ct_upvt
key_part1 = 'usr:'
key_part2 = ':ct_upvt'
for i in xrange(num_users):
    key = key_part1 + str(i) + key_part2
    how_many_cts = random.randint(0, 5)
    
    for ct in xrange(how_many_cts):
        r.sadd(key, random.randint(0, num_circuits-1))



