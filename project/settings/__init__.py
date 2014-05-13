# -*- coding: utf-8 -*-
# Django settings for djangoapp project.

from os.path import dirname, join, realpath
import admin_tools

ROOT_DIR = realpath(join(dirname(__file__), '..', '..'))
PROJECT_DIR = realpath(join(dirname(__file__), '..'))
DATA_DIR = realpath(join(dirname(__file__), '..', '..', 'data'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG
#TEMPLATE_DEBUG = False

ADMINS = (
    ('Worldrat DevOps Team', 'devops@worldrat.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'worldrat',
        'USER': 'worldrat',
        'PASSWORD': 'worldrat',
        'HOST': 'localhost',
        'PORT': '',
    }
}

REDIS = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
HAYSTACK_CONNECTIONS = {
    'default': {
    'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
    'URL': 'http://127.0.0.1:8983/solr'
    },
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Lima'

# IMPORTANT:
# languages should be a mirror of language under user_profile/constants.py
LANGUAGES = (
    ('en', 'English'),
    ('es', 'Español'),
)

LOCALE_PATHS = (
    realpath(join(ROOT_DIR, 'locale')),
)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-ES'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = realpath(join(ROOT_DIR, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = realpath(join(ROOT_DIR, 'static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

##Maybe not used
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
#STATICFILES_FINDERS = (
#    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
#)
##Maybe not used - ENd


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'x^6fahzbxvtrgrrv1(db)-7vc_=m0_of3$*b#&v68z4ieprv5u'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'redirections.middleware.RedirectionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'website.middleware.SetLanguage',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.debug',
    'django.contrib.messages.context_processors.messages',
    'common.context_processors.current_site',
    'circuits.context_processors.circuit_creation_form',
    'website.context_processors.login_link_flag',
    'website.context_processors.registration_link_flag'
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    realpath(join(ROOT_DIR, 'templates')),
)

INSTALLED_APPS = (

    # Django admin_tools
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',

    # Django
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.gis',
    'django.contrib.comments',

    # Deps
    'django_extensions',
    'south',
    'mailer',
    'sorl.thumbnail',
    'celery',
    'kombu.transport.django',
    'djcelery',
    'rosetta',
    'django_countries',
    'debug_toolbar',

    # Apps
    'abstract_mailer',
    'circuits',
    'closed_beta',
    'common',
    'FS_tools',
    'googlemaps_localities',
    'notifications',
    'organizations',
    'places',
    'recsys',
    'redirections',
    'redis_simulation',
    'registration',
    'simulation',
    'stats',
    'suggestions',
    'topics',
    'user_profile',
    'visits',
    'website',
)

ENABLE_HAYSTACK = False
ENABLE_GEOIP = True
ENABLE_DEBUG_TOOLBAR = False
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
STAFF_SOURCES = (0,3)
# 1 =WORLDRAT_USERS
# 2= WORLDRAT_STAFF
# 3 = NEXTSTOP
AUTH_PROFILE_MODULE = 'user_profile.UserProfile'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DEFAULT_CACHE_TIMEOUT = 5

#DEFAULT_AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'
AUTHENTICATION_BACKENDS = ( 'user_profile.auth.backends.EmailAuthentication',
                            'django.contrib.auth.backends.ModelBackend',)
LOGIN_URL = '/login/'

SESSION_COOKIE_NAME = "worldrat_session_id"

# Site prefix
SITE_PREFIX = 'https://worldrat.com'
MEDIA_PREFIX = 'https://worldrat.com/media'
STATIC_PREFIX = 'https://worldrat.com/static'
FACEBOOK_SITE_PREFIX = 'http://files.gnrfan.org/worldrat_demo_app/'
REDIRECTOR_PREFIX = 'http://redirector.worldrat.com'

# Facebook integration
FACEBOOK_APP_ID = '364367280290268'
FACEBOOK_APP_SECRET = '455bee2498ce10d809237efc30c4a701'

# Twitter integration
TWITTER_CONSUMER_KEY = 'oyhdZpq658bbunUEU572gw'
TWITTER_CONSUMER_SECRET = '2LSrbp3b4IFdiK6y4nzgAJlflrCRFT1inoDIgZmaOyQ'

# Foursquare integration
FS_CLIENT_ID = 'A4XD5FLTP5HWQS12FXN1X43HLGIU32TCX1KPYHCLLQD54OYO'
FS_CLIENT_SECRET = 'KAXIZOCVFJZWIFETAS1MRLB0DL1XYS10TDQS2ROAJ3E1YA0Y'

# Registration post processors

REGISTRATION_POST_PROCESSORS = (
    'facebook_integration.postprocessors.facebook_postprocessor',
)

GEOIP_DATABASE = realpath(join(DATA_DIR, 'GeoIP.dat'))

# Persistent session vars
PSV_DICT_NAME = 'persistent_session_vars'

# Email configuration

DEFAULT_FROM_EMAIL = 'no-reply@worldrat.com'
EMAIL_DEFAULT_FROM_VALUE = 'no-reply@worldrat.com'

EMAIL_HOST = 'smtp.sendgrid.net'
#EMAIL_HOST_USER = 'worldrat.tests@gmail.com'
#EMAIL_HOST_PASSWORD = 'w0rldr4t###'
EMAIL_HOST_USER = 'worldrat'
EMAIL_HOST_PASSWORD = 'r4tk1ng'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# ID number scrambler

DECIMAL_SCRAMBLER_DIGITS = [
  '01', '00', '34', '74', '66', '30', '36', '46', '64', '45',
  '89', '60', '19', '52', '50', '10', '47', '81', '53', '32',
  '72', '27', '08', '70', '77', '91', '54', '29', '41', '05',
  '18', '67', '68', '48', '40', '57', '75', '38', '82', '15',
  '06', '96', '42', '22', '03', '80', '93', '37', '04', '58',
  '56', '43', '28', '33', '24', '98', '16', '78', '17', '07',
  '55', '49', '65', '69', '88', '26', '25', '21', '35', '11',
  '85', '61', '31', '84', '87', '02', '90', '86', '76', '20',
  '23', '92', '63', '71', '79', '94', '14', '73', '44', '97',
  '95', '83', '13', '99', '12', '62', '39', '59', '51', '09'
]

DECIMAL_SCRAMBLER_OFFSET = 1000000
DECIMAL_SCRAMBLER_DIGIT_SIZE = 2

#Google API settings
STATIC_MAPS_ROOT = 'https://maps.googleapis.com/maps/api/staticmap'
# API Key for Browser Apps
GOOGLE_API_KEY = 'AIzaSyCOQjIwsy9D-RNZJVs1FRAslQBqTBFsZKg'

GOOGLE_MAPS_API_KEYS = {
    'CLIENT': 'AIzaSyCOQjIwsy9D-RNZJVs1FRAslQBqTBFsZKg',
    'SERVER': 'AIzaSyAhCjvCNNNxgsW4S0Tjk9AYW2AzZMJkmLQ'
}

# Foursquare Token
# mathias@worldrat.com
OAUTH_TOKEN = '14JK5CRWENZ0OEOYVT3B55CBTBVBA1HNTTKAZ3JZCLUILEPT'
# worldrat app
FS_CLIENT_ID='BH1AGHK1ZT2I3B2COXQYRPVRDKZ221BA0HPG1F5QATRT4PYJ'
FS_CLIENT_SECRET='PIA0VOV4NHLEP1BRPUXJA2DF4WXS4H50HZHUCITKC22LE4ZS'
# File to write the JSON categories
FS_CATEGORIES_FILE=realpath(join(STATIC_ROOT ,'foursquare', 'categories.json'))

#Login Settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

# API Settings
API_V1_PREFIX = 'https://worldrat.com/'

# Picture prefix (as called in apps/common/mixins.py)
ASSETS_PREFIX = 'https://worldrat.com/assets/'
ASSETS_PATH_TO_REMOVE = '/media/pictures/'

# imageresizer root directory
IMAGERESIZER_ROOT = realpath(join(MEDIA_ROOT, 'pictures'))
IMAGERESIZER_PATH_TO_REMOVE = '/assets/'
IMAGERESIZER_CACHE_PATH = 'media/cache/'
IMAGERESIZER_CACHE_PREFIX = 'https://worldrat.com/'

THUMB_SQUARE_SIZE = '130'
THUMB_SMALL_SIZE = '180'
THUMB_DEFAULT_CROP = '0px 0px'

ACCOUNT_ACTIVATION_DAYS = 7

# storing models for django.messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

#Closed Beta
CLOSED_BETA_ACTIVE = False
CLOSED_BETA_DESTINATION_VIEW_NAME = 'registration_register'
CLOSED_BETA_INVITATION_PARAM_NAME = 'code'
CLOSED_BETA_DESTINATION_LINK_PROTOCOL = 'https'
INVITATION_MAIL_SUBJECT = u'Worldrat Beta invite'
CLOSED_BETA_DEFAULT_ADDITIONAL_INVITATIONS = 20

CLOSED_BETA_INVITATION_URL = '/invitation/'
CLOSED_BETA_INVITATION_MIDDLEWARE_REDIRECT = CLOSED_BETA_INVITATION_URL

CLOSED_BETA_INVITATION_MIDDLEWARE_EXCEPTED_PATTERNS = (
    r'^/api/v1/',
    r'^/static/',
    r'^/media/',
    r'^/admin/',
    r'^/registration/',
    r'^/',
)

CLOSED_BETA_INVITATION_MIDDLEWARE_EXCEPTED_URIS = (
    CLOSED_BETA_INVITATION_URL,
    LOGIN_URL,
)

# Celery
BROKER_URL = "django://"

# MaxMind Database path
GEO_LITE_PATH = realpath(join(DATA_DIR,'GeoLiteCity.dat'))

# Proxy script configuration

PROXY_SCRIPTS = (
    'http://files.gnrfan.org/scripts/proxy.php',
    'http://barovia.breno.org/proxy.php',
    'http://173.203.205.204/proxy.php'
)

ENABLE_PROXY_SCRIPTS = True

FORBIDDEN_TEMPLATE = '403.html'


# Load local settings

try:
    from local_settings import *
except:
    pass


if ENABLE_HAYSTACK:
    INSTALLED_APPS += ('haystack',)


if ENABLE_DEBUG_TOOLBAR:
    # Add Callback so the staff users can see the Debug Toolbar
    def show_toolbar_for_admin(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar_for_admin,
        'INTERCEPT_REDIRECTS': False,
    }

