try:
    import json
except ImportError:
    import simplejson as json

import sys
import requests
from django.conf import settings
from django.db import transaction
from places.models import Place
from common.utils.debug import writelog
from proxy_scripts import generate_proxied_url
from googlemaps_localities import settings as localities_settings
from googlemaps_localities.models import GoogleMapsAddressComponent

MAX_ITEMS = 25000

@transaction.commit_manually
def run():
    log_path = localities_settings.REVERSE_GEOLOCATION_ERROR_LOG
    places = Place.objects.filter(locality__isnull=True)
    places = places[:MAX_ITEMS]
    for p in places:
        print "Resolving coordinates %s for place %s: %s" % (
            p.get_coordinates_string(), p.pk, p.name
        )
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
                print data['status']
                if data['status'] == 'ZERO_RESULTS':
                    msg = "Zero results at: %s" % url
                    writelog(log_path, msg)
                    continue
                # Aborting executing
                msg = "Aborting executing of script due to error: %s" % (
                    data['status']
                )
                writelog(log_path, msg)
                transaction.commit()
                sys.exit(-1)
        except Exception, e:
            print "Can't parse web service response! aborting..."
            print "URL: %s" % url
            msg = "Non valid JSON at: %s" % url
            writelog(log_path, msg)
            continue

        obj = GoogleMapsAddressComponent.get_or_create_locality_from_json(
            r.content
        )
        if obj is not None:
            p.locality = obj
            p.save()
            msg = (
                "Associating component of type %s and id #%d "
                "with place with id %s"
            )
            print msg % (obj.component_type, obj.pk, p.pk)
            print p.locality
            transaction.commit()
        else:
            print "No locality could be found!!!"

    # We commit any pending changes just to be sure
    transaction.commit()

# Run script
run()
