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
    circuit_updated
)
from recsys.utils.synchronize import RedisSync


def process_circuit_visited(sender, **kwargs):
    from visits.models import Visit
    # Grab circuit
    circuit = sender
    # Grab the request
    request = kwargs.get('request', None)
    # We can't go on if the request is missing
    if request is None:
        return None
    else:
        # Grab the Redis-backed helper class
        rs = RedisSync()
    # Increase the visit counter
    rs.circuit_count_visit(circuit_id=circuit.pk)
    # Add authenticated user as visitor
    if request.user.is_authenticated():
        rs.circuit_update_visitor(
            circuit_id=circuit.pk,
            user_id=request.user.pk
        )
        # add visited circuit to user set of visited circuits
        rs.user_visited_circuits_add(
            user_id=request.user.pk, 
            circuit_id=circuit.pk
        )
    # Record the visit in the database
    Visit.create_visit(
        content_object=circuit,
        request=request
    )


def process_circuit_created(sender, **kwargs):
    # get involved circuit
    circuit = sender
    user_id = circuit.author.pk
    category_id = circuit.category
    # instantiate a RedisSync object
    R = RedisSync()
    R.user_author_circuits_add(user_id=user_id, circuit_id=circuit.pk)
    R.category_in_circuits_add(
        category_value=category_id, 
        circuit_id=circuit.pk
    )
    R.all_circuits_add(circuit_id=circuit.pk)


def process_circuit_deleted(sender, **kwargs):
    # get involved circuit
    circuit = sender
    user_id = circuit.author.pk
    category_id = circuit.category
    # instantiate a RedisSync object
    R = RedisSync()
    R.user_author_circuits_rmv(user_id=user_id, circuit_id=circuit.pk)
    R.category_in_circuits_rmv(
        category_value=category_id, 
        circuit_id=circuit.pk
    )
    R.all_circuits_rmv(circuit_id=circuit.pk)


def process_circuit_updated(sender, **kwargs):
    # get involved circuit
    circuit = sender
    category_id = circuit.category
    # instantiate a RedisSync object
    R = RedisSync()
    R.category_in_circuits_rmv(
        category_value=category_id, 
        circuit_id=circuit.pk
    )


# Conecting signals ===========================================================
circuit_visited.connect(
    process_circuit_visited, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)

circuit_created.connect(
    process_circuit_created, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)

circuit_deleted.connect(
    process_circuit_deleted, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)

circuit_updated.connect(
    process_circuit_updated, 
    dispatch_uid=str(uuid.uuid4()),
    weak=False
)