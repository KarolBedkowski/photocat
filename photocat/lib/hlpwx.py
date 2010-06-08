# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2010'
__version__ = '2010-06-08'


from contextlib import contextmanager

import wx


@contextmanager
def with_wait_cursor():
	wx.SetCursor(wx.HOURGLASS_CURSOR)
	try:
		yield
	finally:
		wx.SetCursor(wx.STANDARD_CURSOR)



# vim: encoding=utf8: ff=unix:
