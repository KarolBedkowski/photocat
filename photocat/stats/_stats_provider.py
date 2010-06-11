# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-11"


import weakref

from photocat.model import Directory, Collection, FileImage


class StatsProvider(object):
	name = ''

	def __init__(self):
		self._cache = None
		self._progress_cb = None

	@property
	def need_compute(self):
		return not (self._cache)

	def _compute_stats(self, objects):
		pass

	def get_stats(self, objects, progress_cb=None):
		self._progress_cb = weakref.ref(progress_cb) if progress_cb else None
		if not self._cache:
			self._cache = dict(self._compute_stats(objects))
		return self._cache

	def _get_items(self, objects):
		for obj in objects:
			if isinstance(obj, Collection):
				for disk in obj.disks:
					if self._progress_cb and self._progress_cb():
						self._progress_cb()(disk.name)
					for item in self._get_items_in_dir(disk):
						yield item
			elif isinstance(obj, Directory):
				for item in self._get_items_in_dir(obj):
					yield item
			elif isinstance(obj, FileImage):
				yield obj

	def _get_items_in_dir(self, directory):
		for subdir in directory.subdirs:
			for item in self._get_items_in_dir(subdir):
				yield item
		for img in directory.files:
			yield img


# vim: encoding=utf8: ff=unix:
