# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-05"


from photocat.model import Directory, Collection, FileImage

from ._stats_provider import StatsProvider


class BasicStats(StatsProvider):
	name = _('Basic')

	def __init__(self):
		StatsProvider.__init__(self)
		self._disks = 0
		self._dirs = 0
		self._files = 0

	def _compute_stats(self, objects):
		self._get_items(objects)
		yield _('Basic'), [((0, _('Disks')), self._disks, None),
				((1, _('Directories')), self._dirs, None),
				((2, _('Files')), self._files, None),
		]

	def _get_items(self, objects):
		for obj in objects:
			if isinstance(obj, Collection):
				self._find_itmes_in_collection(obj)
			elif isinstance(obj, Directory):
				self._find_items_in_dir(obj)

	def _find_itmes_in_collection(self, collection):
		self._disks += len(collection.disks)
		for disk in collection.disks:
			self._find_items_in_dir(disk)

	def _find_items_in_dir(self, directory):
		self._dirs += len(directory.subdirs)
		for subdir in directory.subdirs:
			self._find_items_in_dir(subdir)
		self._files += len(directory.files)



# vim: encoding=utf8: ff=unix:
