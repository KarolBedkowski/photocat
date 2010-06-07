# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2010'
__version__ = '2010-06-07'


import locale

_ENC = locale.getpreferredencoding(do_setlocale=False)


def from_locale(str_):
	return str_.decode(_ENC, 'replace')



# vim: encoding=utf8: ff=unix:
