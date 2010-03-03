# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (checkshowmaininterface)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


class LoadFileError(Exception):
	pass


class InvalidFileError(LoadFileError):
	pass


class SaveFileError(Exception):
	pass


# vim: encoding=utf8: ff=unix:
