# -*- coding: utf-8 -*-

"""
 Photo Catalog v 1.0  (photocat)
 Copyright (c) Karol Będkowski, 2004-2010

 This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-04"



STATS_PROVIDERS = {}


from .exif import ExifLens

STATS_PROVIDERS[ExifLens.name] = ExifLens



# vim: encoding=utf8: ff=unix:
