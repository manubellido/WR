DEBUG=True

ADMINS = (
    ('Your name', 'username@worldrat.com'),
)

API_V1_PREFIX = 'http://localhost:8000/'
ASSETS_PREFIX = 'http://localhost:8000/assets/'
IMAGERESIZER_CACHE_PREFIX = 'http://localhost:8000/'

CLOSED_BETA_ACTIVE = False
ENABLE_DEBUG_TOOLBAR = False
CACHES = {}

if CLOSED_BETA_ACTIVE = False:
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    )
