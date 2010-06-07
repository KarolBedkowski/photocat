# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2010'
__version__ = '2010-06-07'


import subprocess
import os
import logging


_LOG = logging.getLogger(__name__)


def open_file(filepath):
	''' Try to open file by default application'''
	_LOG.debug('open_file(%s)' % filepath)
	if not os.path.isfile(filepath):
		return
	if os.name == 'mac':
		subprocess.call(('open', filepath))
	elif os.name == 'nt':
		subprocess.call(('start', filepath))
	elif os.name == 'posix':
		subprocess.call(('xdg-open', filepath))
	else:
		_LOG.warn('open_file: unknown os %s' % os.name)



# vim: encoding=utf8: ff=unix:
