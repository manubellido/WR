# -*- coding: utf-8 -*-

"""
imageresizer entry points
"""

import os
import time
import mimetypes
import hashlib

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET
from django.views.static import serve
from django.utils.http import http_date, quote_etag

from imageresizer.conf import settings
from sorl.thumbnail import default
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.images import ImageFile

# This import writes default values into settings
from imageresizer.utils import make_geometry_string
from imageresizer import constants


@require_GET
def thumbnail(request, root_dir=None):
    """
    Scales (conserving aspect ratio) a requested image with given width, height
    and orientation
    """
    width = request.GET.get('width', None)
    height = request.GET.get('height', None)
    crop = request.GET.get('crop', None)
    orientation = request.GET.get('orientation', constants.ORIENTATION_DEFAULT)
    geometry_string = make_geometry_string(width, height)
    if root_dir is None:
        root_dir = settings.IMAGERESIZER_ROOT
    resource_path = request.path.replace(
        settings.IMAGERESIZER_PATH_TO_REMOVE, '', 1
    )
    path = os.path.realpath(os.path.join(root_dir, resource_path))
    if not os.path.exists(path):
        raise Http404
    if geometry_string is None:
        image = ImageFile(path, storage=default.storage)
        image.set_size()
        geometry_string = make_geometry_string(image.width, image.height)
    thumbnail = get_thumbnail(path, geometry_string,
            ll_transverse=True \
                if orientation == constants.ORIENTATION_LANDSCAPE \
                else False)
    mimetype, encoding = mimetypes.guess_type(path)
    response = HttpResponse(thumbnail.read(), mimetype=mimetype)
    last_modified = http_date(
        time.mktime(
            thumbnail.storage.modified_time(thumbnail.name).timetuple()
        )
    )
    response['Last-Modified'] = last_modified
    response['ETag'] = quote_etag(hashlib.sha1(last_modified).hexdigest())
    response['Content-Length'] = thumbnail.storage.size(thumbnail.name)
    response['Accept-Ranges'] = 'bytes'
    return response
