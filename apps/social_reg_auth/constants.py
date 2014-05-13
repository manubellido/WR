# -*- coding: utf-8 -*-

# Facebook stuff
FACEBOOK_PERMISSIONS = (
    'email',
)

FACEBOOK_BASE_AUTH_URL = 'https://www.facebook.com/dialog/oauth'
FACEBOOK_BASE_ATOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
FACEBOOK_BASE_GRAPH_API_URL = 'http://graph.facebook.com/'

# TODO: @mathiasbc change this line to proper direction
SITE_PREFIX = 'http://dev.worldrat.com/'

LOGIN_URL='/social_auth/twitter/login'
LOGOUT_URL='/social_auth/twitter/logout'
