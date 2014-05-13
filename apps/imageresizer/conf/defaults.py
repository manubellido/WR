# -*- coding:utf-8 -*-
"""
imageresizer default settings
Mirrors some useful settings from sorl.thumbnail
"""
from django.conf import settings

# When True ThumbnailNode.render can raise errors
IMAGERESIZER_DEBUG = False

# Backend
IMAGERESIZER_BACKEND = 'imageresizer.backend.thumbnail_backend.ThumbnailBackend'

# Key-value store, ships with:
# sorl.thumbnail.kvstores.cached_db_kvstore.KVStore
# sorl.thumbnail.kvstores.redis_kvstore.KVStore
# Redis requires some more work, see docs
IMAGERESIZER_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'

# Engine, ships with:
# sorl.thumbnail.engines.convert_engine.Engine
# sorl.thumbnail.engines.pil_engine.Engine
# sorl.thumbnail.engines.pgmagick_engine.Engine
# convert is preferred but requires imagemagick or graphicsmagick, see docs
IMAGERESIZER_ENGINE = 'imageresizer.backend.convert_engine.Engine'

# Path to Imagemagick or Graphicsmagick ``convert`` and ``identify``.
IMAGERESIZER_CONVERT = 'convert'
IMAGERESIZER_IDENTIFY = 'identify'

# Storage for the generated thumbnails
IMAGERESIZER_STORAGE = 'imageresizer.backend.storage.FileSystemStorage'

# Redis settings
IMAGERESIZER_REDIS_DB = 0
IMAGERESIZER_REDIS_PASSWORD = ''
IMAGERESIZER_REDIS_HOST = 'localhost'
IMAGERESIZER_REDIS_PORT = 6379

# Cache timeout for ``cached_db`` store. You should probably keep this at
# maximum or ``0`` if your caching backend can handle that as infinate.
IMAGERESIZER_CACHE_TIMEOUT = 3600 * 24 * 365 * 10 # 10 years

# Key prefix used by the key value store
IMAGERESIZER_KEY_PREFIX = 'imageresizer'

# Thumbnail filename prefix
IMAGERESIZER_PREFIX = 'cache/'

# Image format, common formats are: JPEG, PNG
# Make sure the backend can handle the format you specify
IMAGERESIZER_FORMAT = 'PNG'

# Colorspace, backends are required to implement: RGB, GRAY
# Setting this to None will keep the original colorspace.
IMAGERESIZER_COLORSPACE = 'RGB'

# Should we upscale images by default
IMAGERESIZER_UPSCALE = True

# Quality, 0-100
IMAGERESIZER_QUALITY = 95

# This means sorl.thumbnail will generate and serve a generated dummy image
# regardless of the thumbnail source content
IMAGERESIZER_DUMMY = False

# Thumbnail dummy (placeholder) source. Some you might try are:
# http://placekitten.com/%(width)s/%(height)s
# http://placekitten.com/g/%(width)s/%(height)s
# http://placehold.it/%(width)sx%(height)s
IMAGERESIZER_DUMMY_SOURCE = 'http://placekitten.com/%(width)s/%(height)s'

# Sets the source image ratio for dummy generation of images with only width
# or height given
IMAGERESIZER_DUMMY_RATIO = 1.5

# Absolute filesystem path to the directory that will hold image files,
# in general.
IMAGERESIZER_ROOT = settings.MEDIA_ROOT
