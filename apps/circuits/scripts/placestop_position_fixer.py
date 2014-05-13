# -*- coding: utf-8 -*-
"""
Fixes the position of all CircuitStops on a Circuit so that the stay 
visualy nice in the googlemaps display canvas
"""

from circuits.models import Circuit, CircuitStop
from places.models import Place

def run():
    all_cts = Circuit.objects.all()

    for ct in all_cts:
        print "fixing stops on circuit %s" % ct
        stops = []
        for stop in ct.circuit_stops.all():
            stops.append(stop)

        # super magical sorting function
        stops.sort(key=lambda CircuitStop: CircuitStop.place.coordinates.x)

        # set new position to stop
        counter = 1
        for stop in stops:
            stop.position = counter
            stop.save()
            counter += 1

        #for stop in ct.circuit_stops.all().order_by('position'):
        #    print "%s %s" % (stop.position, ct.name)

if __name__ == "__main__":
    run()

