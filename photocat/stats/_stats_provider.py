# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-05"


class StatsProvider(object):
	name = ''

	def __init__(self):
		self._cache = None

	def _compute_stats(self, objects):
		pass

	def get_stats(self, objects):
		if not self._cache:
			self._cache = dict(self._compute_stats(objects))
		return self._cache




# vim: encoding=utf8: ff=unix:
