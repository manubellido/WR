# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from googlemaps_localities.api import resources

urlpatterns = patterns('',
    url(
        r'^gmacs/lookup/?$',
        resources.GMACLookupController.as_view(),
        name='gmac_lookup_controller_resource'
    ),
    url(
        r'^gmacs/lookup_by_coords/?$',
        resources.GMACLookupByCoordsFunction.as_view(),
        name='gmac_lookup_by_coords_function_resource'
    ),
)
