#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
pc.engine.efile
-- engine do obsługi plików

Photo Catalog v 1.0  (pc)
Copyright (c) Karol Będkowski, 2004, 2005, 2006

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'

import os.path
import logging
_LOG = logging.getLogger(__name__)


def get_file_date_size(path):
	''' get (file data, file size) for @path '''
	return os.path.getmtime(path), os.path.getsize(path)


# vim: encoding=utf8: ff=unix:
