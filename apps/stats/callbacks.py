# -*- coding: utf-8 -*-
import uuid

from circuits.signals import (
    circuit_visited,
    circuit_remixed,
    circuit_remix_deleted,
    circuit_favorited,
    circuit_unfavorited,
    circuit_created,
    circuit_deleted,
    circuit_updated,
)

from stats.synchronize import RedisStatsSync

def process_add_fav_user(sender, **kwargs):
    """ 
    processes add favorite circuit signal
    """
    # Grab the user_id
    user_id = kwargs.get('user_id', None)
    # We can't go on if not user_id
    if user_id is None:
        return None
    # Redis-backend helper class
    R = RedisStatsSync()
    # Increase the circuit favorites counter
    R.incr_circuit_fav_count(circuit_id=sender.pk)
    # add user_id to circuit favoriting set
    R.add_favoriting_user_id(circuit_id=sender.pk, user_id=user_id)
    # add circuit_id to user favorites set
    R.user_fav_circuits_add(circuit_id=sender.pk, user_id=user_id)

def process_rm_fav_user(sender, **kwargs):
    """ 
    processes remove favorite circuit signal
    """   
    # Grab the user_id
    user_id = kwargs.get('user_id', None)
    # We can't go on if not user_id
    if user_id is None:
        return None
    # Redis-backend helper class
    R = RedisStatsSync()
    # Increase the circuit favorites counter
    R.decr_circuit_fav_count(circuit_id=sender.pk)
    # remove user_id to circuit favoriting set
    R.rm_favoriting_user_id(circuit_id=sender.pk, user_id=user_id)
    # remove circuit_id from user set of favorites
    R.user_fav_circuits_rmv(circuit_id=sender.pk, user_id=user_id)

def process_add_remixed_circuit(sender, **kwargs):
    """ 
    processes remix circuit signal for adding 
    """
    # Grab the remixed circuit PK
    remixed_id = kwargs.get('remixed_circuit_id', None)
    # We can't go on if not remixed_circuit_id
    if remixed_id is None:
        return None
    # Redis-backend helper class
    R = RedisStatsSync()
    # Increase the circuit remix counter
    R.incr_circuit_remix_count(circuit_id=sender.pk)
    # add remixed circuit to circuit set
    R.add_remixed_circuit_id(original_id=sender.pk, remixed_id=remixed_id)

def process_rm_remixed_circuit(sender, **kwargs):
    """ 
    processes remix circuit signal for deleting
    """      
    # Grab the remixed circuit PK
    remixed_id = kwargs.get('remixed_circuit_id', None)
    # We can't go on if not remixed_circuit_id
    if remixed_id is None:
        return None
    # Redis-backend helper class
    R = RedisStatsSync()
    # decrease the circuit remix counter
    R.decr_circuit_remix_count(circuit_id=sender.remixed_from.pk)
    # remove remixed circuit to circuit set
    R.rm_remixed_circuit_id(
        original_id=sender.remixed_from.pk, 
        remixed_id=remixed_id
    )

# Conect signals
circuit_remixed.connect(
    process_add_remixed_circuit, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)

circuit_remix_deleted.connect(
    process_rm_remixed_circuit, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)

circuit_favorited.connect(
    process_add_fav_user, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)

circuit_unfavorited.connect(
    process_rm_fav_user, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)