# -*- coding: utf-8 -*-

"""
Misc utils
"""

def make_geometry_string(width, height):
    try:
        width = int(width)
    except TypeError:
        width = None
    try:
        height = int(height)
    except TypeError:
        height = None
    if width is None:
        width = height
    if height is None:
        height = width
    if width is not None:
        return '%ix%i' % (width, height)
    return None
