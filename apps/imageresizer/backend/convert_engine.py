#-*- coding:utf-8 -*-
"""
Extends the original "convert" engine to support low-level parameters
"""
import os
from subprocess import Popen
from tempfile import mkstemp

from django.utils.datastructures import SortedDict
from django.utils.encoding import smart_str

from sorl.thumbnail.base import EXTENSIONS
from sorl.thumbnail.conf import settings
from sorl.thumbnail.engines.convert_engine import Engine as BaseEngine

from imageresizer import constants

class Engine(BaseEngine):
    """
    Image object is a dict with source path, options and size
    """
    def write(self, image, options, thumbnail):
        """
        Writes the thumbnail image
        """
        handle, out = mkstemp(suffix='.%s' % EXTENSIONS[options['format']])
        args = [settings.THUMBNAIL_CONVERT, image['source']]
        for k, v in image['options'].iteritems():
            args.append('-%s' % k)
            if v is not None:
                args.append('%s' % v)
        for k, v in (
                (k, v) 
                for k, v in options.iteritems() 
                if isinstance(k, (str, unicode, )) and k.startswith(
                    constants.LOW_LEVEL_PREFIX)):
            if v not in (False, None):
                args.append('-%s' % k[
                        len(constants.LOW_LEVEL_PREFIX):].replace('_', '-'))
                if v is not True:
                    args.append('%s' % v)
        args.append(out)
        args = map(smart_str, args)
        p = Popen(args)
        p.wait()
        with open(out, 'r') as fp:
            thumbnail.write(fp.read())
        os.close(handle)
        os.remove(out)
        os.remove(image['source']) # we should not need this now
