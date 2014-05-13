import difflib
from googlemaps_localities.models import GoogleMapsAddressComponent as GMAC
from common.utils.maxmind import get_locality_string

def match_gmac(ip):

    data = get_locality_string(ip)

    if data is None:
        return None

    data = data.split(',')
    country = data[2].strip()
    state = data[1].strip()
    city = data[0].strip()
    gmacs = GMAC.objects.all()

    best_match = 0.0
    best_gmac = None
    for mac in gmacs:
        dis = difflib.SequenceMatcher(None, mac.long_name, country).ratio()
        if dis > best_match:
            best_match = dis
            best_gmac = mac

    if best_match > 0.8 and city != 'None':
        sons = GMAC.get_all_children_from_redis(best_gmac.pk)
        best_match = 0.0
        best_gmac = None
        for son in sons:
            dis = difflib.SequenceMatcher(None, son.long_name, city).ratio()
            if dis > best_match:
                best_match = dis
                best_gmac = son
        return best_gmac

    elif best_match > 0.8 and state != 'None':
        best_match = 0.0
        best_gmac = None
        for son in sons:
            dis = difflib.SequenceMatcher(None, son.long_name, state).ratio()
            if dis > best_match:
                best_match = dis
                best_gmac = son
        return best_gmac
    else:
        return best_gmac

