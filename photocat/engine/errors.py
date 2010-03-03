#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
photocat.engine.errors
-- klasy wyjątków wyrzucanych przez engine

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004, 2005, 2006

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


import logging

_LOG = logging.getLogger(__name__)


class UpdateDiskError(StandardError):
	''' UpdateDiskError '''
	pass


class OpenCatalogError(StandardError):
	''' OpenCatalogError '''
	pass


# vim: encoding=utf8: ff=unix:
