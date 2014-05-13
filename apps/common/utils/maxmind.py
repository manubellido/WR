from django.conf import settings

if settings.ENABLE_GEOIP:
    import GeoIP

    def get_locality_string(ip):
        """
        Using MindMax GeoLiteCity DB, resolve an IP address to a country, state,
        city
        """
        gi = GeoIP.open(settings.GEO_LITE_PATH, GeoIP.GEOIP_STANDARD)
        gir = gi.record_by_addr(ip)

        if gir != None:
            #print str(gir)
            city = gir['city']
            region = gir['region_name']
            country = gir['country_name']
            return "%s, %s, %s" % (city, region, country)
        else:
            return None

    def get_locality_coords(ip):
        """
        Using MindMax GeoLiteCity DB, resolve an IP address to a lat and lng
        """
        gi = GeoIP.open(settings.GEO_LITE_PATH, GeoIP.GEOIP_STANDARD)
        gir = gi.record_by_addr(ip)

        if gir != None:
            lat = gir['latitude']
            lng = gir['longitude']
            return "%s, %s" % (lat, lng)
        else:
            return None
else:
    def get_locality_string(ip):
        return None

    def get_locality_coords(ip):
        return None
