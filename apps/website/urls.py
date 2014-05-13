# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from website.views import show_home, test_recsys, change_lang


urlpatterns = patterns('website.views',
    url(r'^privacy_policy/$', 'privacy_policy', name='privacy_policy'),
    url(r'^terms_of_use/$', 'terms_of_use', name='terms_of_use'),
    url(r'^who_we_are/$', 'who_we_are', name='who_we_are'),
    url(r'^about/$', 'about_worldrat', name='about_worldrat'),
    url(r'^change_location/$', 'change_location', name='change_location'),
    url(
        r'^routes/recommended/(?P<gmac_slug>[\/\w_-]+)/$',
        test_recsys,
        name='home_loc'
    ),
    url(r'^routes/recommended/$', test_recsys, name='recommended_circuits'),
    url(r'^$', show_home, name='home'),
    url(r'^language/(?P<lang_id>\d+)/?$', change_lang, name='change_lang'),

)
