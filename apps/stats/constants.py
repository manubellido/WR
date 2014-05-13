# -*- coding: utf-8 -*-

"""
Constants keys on Redis for Circuit Recsys
"""

# All these constants should be upper case
# No constant should have ':' in it, we should try
# to normalize all methods RedisSync to use ':'.join
# so the colon isn't hardcoded in the constant.

from recsys.circuits.constants import (
    usr_fav_ct_1,
    usr_fav_ct_2,
)

# IMPORTED
# Definition: user favorite circuits
# type: set
# key = usr:[usr_id]:fav_cts 
#usr_fav_ct_1 = 'usr:'
#usr_fav_ct_2 = ':fav_cts'

# Definition: number of favorites that a circuit has
# type: counter
# key = ct:[ct_id]:nmbr_favs
CIRCUIT_NMBR_FAVS_1 = 'ct'
CIRCUIT_NMBR_FAVS_2 = 'nmbr_favs'

# Definition: users that favorited a circuit
# type: set
# key = ct:[ct_id]:fav_usrs
CIRCUIT_FAV_USRS_1 = 'ct'
CIRCUIT_FAV_USRS_2 = 'fav_usrs'

# Definition: number of times a circuit has been remixed
# type: counter
# key = ct:[ct_id]:nmbr_rmx
CIRCUIT_NMBR_RMX_1 = 'ct'
CIRCUIT_NMBR_RMX_2 = 'nmbr_rmx'

# Definition: circuits that has been remixed from original_circuit
# type: set
# key = ct:[ct_id]:rmx_cts
CIRCUIT_RMX_CTS_1 = 'ct'
CIRCUIT_RMX_CTS_2 = 'rmx_cts'



