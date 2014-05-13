# -*- coding: utf-8 -*-
import uuid

from django.db.models.signals import post_save
from circuits.models import CircuitStop
from circuits.tasks import add_gmac_to_stop_and_redis_sync


def stop_post_save(sender, instance, **kwargs):
    # FIXME: signal is being send 2 times, check for it
    # send celery task
    add_gmac_to_stop_and_redis_sync.apply_async(
        kwargs={
            'circuitstop_id':instance.pk,
        },
    )
        
# connecting signal ===========================================================
post_save.connect(
    stop_post_save,
    sender=CircuitStop,
    dispatch_uid=str(uuid.uuid4())
)