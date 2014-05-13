# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from website.api import resources

urlpatterns = patterns('',
    url(r'^search/more',
        resources.SearchMoreFunction.as_view(),
        name='search_more'
    ),
)




