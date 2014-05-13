# -*- coding: utf-8 -*-

from django.conf import settings
from sorl.thumbnail import get_thumbnail


class ObjectWithPictureMixin(object):

    def get_picture(self, size):
        url = ''
        ratio_hw = 100

        if not self.picture:
            return {
                'url': url,
                'ratio_hw': ratio_hw,
            }

        try:
            im = get_thumbnail(self.picture.file, size)
            url = '/'.join([
                settings.IMAGERESIZER_CACHE_PREFIX.rstrip('/'),
                im.url.lstrip('/'),
            ])
            ratio_hw = 100 * im.height / im.width
        except IOError:
            pass

        return {
            'url': url,
            'ratio_hw': ratio_hw,
        }

    def get_picture_url(self, size=None):
        """
        Returns the fully qualified URL to the picture
        of the model object as an asset available as a
        thumbnail that gets dinamically created with the
        requested dimensions.
        """
        if not self.picture:
            return None

        if size is None:
            picture_url = self.picture.url \
                .replace(settings.ASSETS_PATH_TO_REMOVE, '').lstrip('/')
        else:
            try:
                im = get_thumbnail(self.picture.file, size)
                picture_url = im.url.lstrip('/')
            except IOError:
                picture_url = ''

        return ''.join([
            settings.IMAGERESIZER_CACHE_PREFIX,
            picture_url
        ])
