# -*- coding: utf-8 -*-
"""
One-time execution script to synchronize everything on relational database 
to Redis sets
"""
from django.contrib.auth.models import User
from circuits.models import Circuit
from stats.synchronize import RedisStatsSync

def execute():
    R = RedisStatsSync()

    all_users = User.objects.all()
    for us in all_users:
        for cat in us.categories.all():
            # user following category_id set
            R.user_category_follow_add(
                category_value=cat.category, 
                user_id=us.pk
            )

    all_cts = Circuit.objects.all()
    for ct in all_cts:
        # circuits set
        R.all_circuits_add(ct.pk)
        # user author circuits
        R.user_author_circuits_add(circuit_id=ct.pk, user_id=ct.author.pk)
        # circuit categories set
        R.category_in_circuits_add(category_value=ct.category, circuit_id=ct.pk)
        # favs counter
        R.set_circuit_fav_count(
            circuit_id=ct.pk, 
            number=ct.follower_profiles.count()
        )
        # remix counter
        R.set_circuit_remix_count(
            circuit_id=ct.pk,
            number=Circuit.objects.filter(remixed_from=ct).count()
        )
        # circuit favoriting users
        for up in ct.follower_profiles.all():
            # add user_id to circuit set
            R.add_favoriting_user_id(circuit_id=ct.pk, user_id=up.user.pk)
            # add circuit_id to user favorites set
            R.user_fav_circuits_add(circuit_id=ct.pk, user_id=up.user.pk)
        # check if circuit is remix of some other circuit
        if ct.remixed_from:
            R.add_remixed_circuit_id(
                original_id=ct.remixed_from.pk,
                remixed_id=ct.pk
            )

