# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-07"


import os.path

from photocat.model import Directory, Collection

from ._stats_provider import StatsProvider


class BasicStats(StatsProvider):
	name = _('Basic')

	def __init__(self):
		StatsProvider.__init__(self)
		self._disks = 0
		self._dirs = 0
		self._files = 0
		self._dirs_size = {}
		self._dirs_image_cnt = {}
		self._disk_image_cnt = {}
		self._file_types = {}

	def _compute_stats(self, objects):
		self._get_items(objects)
		yield _('Basic'), [((0, _('Disks')), self._disks, None),
				((1, _('Directories')), self._dirs, None),
				((2, _('Files')), self._files, None),
		]
		yield _("Dirs by size"), _compute_stats(self._dirs_size)
		yield _("Dirs by images count"), _compute_stats(self._dirs_image_cnt)
		yield _("Disks by images count"), _compute_stats(self._disk_image_cnt)
		yield _("File formats"), _compute_stats(self._file_types)

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
		disk_name = directory.disk.name
		dir_path = disk_name + ':/' + directory.path
		if directory.files:
			self._files += len(directory.files)
			self._dirs_size[dir_path] = directory.directory_size_sumary
			self._dirs_image_cnt[dir_path] = len(directory.files)
			self._disk_image_cnt[disk_name] = self._disk_image_cnt.get(
					disk_name, 0) + len(directory.files)
			for img in directory.files:
				ext = (('.' in img.name) and \
						os.path.splitext(img.name)[-1].lower()[1:]) or ''
				self._file_types[ext] = self._file_types.get(ext, 0) + 1


def _compute_stats(data):
	all_cnt = float(sum(data.itervalues()))
	cnts = sorted((cnt, key) for key, cnt in data.iteritems())
	return [((idx, key), cnt, cnt / all_cnt) for idx, (cnt, key)
			in enumerate(cnts)]


# vim: encoding=utf8: ff=unix:
