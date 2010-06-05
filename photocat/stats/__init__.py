# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-05"


from ._stats_provider import StatsProvider
from .exif import ExifLens
from .basic import BasicStats


STATS_PROVIDERS = StatsProvider.__subclasses__()



# vim: encoding=utf8: ff=unix:
