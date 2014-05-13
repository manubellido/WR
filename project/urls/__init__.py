# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from website import views

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^assets/', include('imageresizer.urls')),
    url(r'^routes/', include('circuits.urls')),
    url(r'^admin_tools/', include('admin_tools.urls')),
    url(r'^users/', include('user_profile.urls')),
    url(r'^facebook/', include('facebook.urls')),
    url(r'^twitter/', include('twitter.urls')),
    url(r'^foursquare/', include('foursquare_oauth.urls')),
    url(r'^activity/', include('notifications.urls')),
    url(r'^settings/', include('user_profile.settings_urls')),
    url(r'^registration/', include('user_profile.registration.urls')),
    url(r'^social_auth/', include('social_reg_auth.urls')),
    url(r'^api/v1/', include('urls.api')),

)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )

if 'haystack' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^search/', views.haystack_search, name='haystack_search'),
    )
else:
    urlpatterns += patterns('',
        url(r'^search/',views.show_home , name="haystack_search"),
    )
if settings.DEBUG or getattr(settings, "STATIC_GERMAN", False):
    from django.views.static import serve
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$',
            serve, {
                'document_root': settings.STATIC_ROOT,
                'show_indexes': True
            }
        ),
        url(r'^media/(?P<path>.*)$',
            serve, {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True
            }
        ),
    )

urlpatterns += patterns('',
    #url(r'^', include('closed_beta.urls')),
    url(r'^', include('user_profile.auth.urls')),
    url(r'^', include('website.urls')),
)
