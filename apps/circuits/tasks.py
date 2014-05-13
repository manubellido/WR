# -*- coding: utf-8 -*-

import simplejson as json
import requests

from django.conf import settings
from common.utils.debug import writelog
from proxy_scripts import generate_proxied_url
from googlemaps_localities import settings as localities_settings
from googlemaps_localities.models import GoogleMapsAddressComponent
from circuits.models import CircuitStop
from recsys.utils.synchronize import RedisSync
from celery.task import task


@task
def add_gmac_to_stop_and_redis_sync(stop_id):
    log_path = localities_settings.REVERSE_GEOLOCATION_ERROR_LOG
    if CircuitStop.objects.filter(pk=stop_id).exists():
        CS = CircuitStop.objects.get(pk=stop_id)
    else:
        return

    # get place
    p = CS.place
    # if place has locality, do nothing
    if p.locality is not None:
        # sync to Redis
        R = RedisSync()
        R.gmac_contains_circuits(p.locality.pk, instance.circuit.pk)
        return

    url = ''.join([
        'http://maps.googleapis.com/maps/api/geocode/json?',
        'latlng=%s&sensor=false' % (p.get_coordinates_string())
    ])
    if settings.ENABLE_PROXY_SCRIPTS:
        url = generate_proxied_url(url)
    r = requests.get(url)
    try:
        data = json.loads(r.content)
        if 'results' in data and len(data['results']) == 0:
            #print data['status']
            if data['status'] == 'ZERO_RESULTS':
                msg = "Zero results at: %s" % url
                writelog(log_path, msg)
                return
            # Aborting executing
            msg = "Aborting executing of script due to error: %s" % (
                data['status']
            )
            writelog(log_path, msg)
            return
    except Exception, e:
        msg = "Non valid JSON at: %s: %s" % (url, e)
        writelog(log_path, msg)
        return

    obj = GoogleMapsAddressComponent.get_or_create_locality_from_json(
        r.content
    )
    if obj is not None:
        p.locality = obj
        p.save()
        # sync to Redis
        R = RedisSync()
        R.gmac_contains_circuits(obj.pk, CS.circuit.pk)
