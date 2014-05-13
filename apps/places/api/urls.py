# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from places.api import resources

urlpatterns = patterns('',
    url(
        r'^places/(?P<place_id>[\w]+)$', 
        resources.PlaceResource.as_view(), 
        name='place_resource'
    ),
    url(
        r'^places/foursquare/categories/(?P<place_type_id>[\w]+)/?$', 
        resources.PlaceCategoryResource.as_view(), 
        name='place_type_resource'
    ),
    url(
        r'^places/foursquare/categories/?$', 
        resources.PlaceCategoryCollection.as_view(), 
        name='place_categories_resource'
    ),
    url(
        r'^places/(?P<place_id>[\w]+)/is_done/?$',
        resources.IsDonePlaceFunction.as_view(),
        name='is_done_function_resource'
    ),
    url(
        r'^places/(?P<place_id>[\w]+)/add_done/?$',
        resources.AddDonePlaceController.as_view(),
        name='add_done_controller_resource'
    ),
    url(
        r'^places/(?P<place_id>[\w]+)/remove_done/?$',
        resources.RemoveDonePlaceController.as_view(),
        name='remove_done_controller_resource'
    ),
)
