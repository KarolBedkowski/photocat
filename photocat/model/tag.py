# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2007'
__revision__ = '$Id$'


from photocat.model.file_image import FileImage
from photocat.lib.hlpweakref import create_weakref_proxy


class Tag(object):
	__slots__ = ('name', 'files', 'dirs', 'catalog', 'tree_node')

	def __init__(self, name=None, catalog=None):
		self.name = name
		self.files = []
		self.dirs = []
		self.catalog = catalog
		self.tree_node = None

	@property
	def files_count(self):
		return len(self.files)

	@property
	def dirs_count(self):
		return len(self.dirs)

	@property
	def count(self):
		return len(self.dirs) + len(self.files)

	@property
	def caption(self):
		return '%s (%d/%d)' % (self.name, len(self.files), len(self.dirs))

	##########################################################################

	def remove_item(self, item):
		if isinstance(item, FileImage):
			if item in self.files:
				self.files.remove(item)

		elif item in self.dirs:
			self.dirs.remove(item)

	def add_item(self, item):
		if isinstance(item, FileImage):
			self.files.append(create_weakref_proxy(item))

		else:
			self.dirs.append(create_weakref_proxy(item))

	def update_items_on_delete(self):
		name = self.name
		for ifile in self.files:
			ifile.tags.remove(name)

		for directory in self.dirs:
			directory.tags.remove(name)

###############################################################################


class Tags(object):
	FV3_CLASS_NAME = 1048576 + 4

	__slots__ = ('_tags', 'catalog', 'current_tags_nodes', 'tree_node')

	def __init__(self, catalog):
		self._tags = {}
		self.catalog = create_weakref_proxy(catalog)
		self.current_tags_nodes = []
		self.tree_node = None

	def __getitem__(self, key, default=None):
		return self._tags.get(key, default)

	def __settem__(self, key, value):
		self._tags[key] = value

	##########################################################################

	def _get_tags(self):
		return self._tags.keys()

	def _set_tags(self, tags):
		# usuniecie brakujących
		to_del = []
		for tag, tagobj in self._tags.iteritems():
			if tag not in tags:
				tagobj.update_items_on_delete()
				to_del.append(tag)

		for tag in to_del:
			self._tags.pop(tag)

		# dodanie nowych
		for tag in tags:
			if tag not in self._tags:
				self._tags[tag] = Tag(tag, self.catalog)

	tags = property(_get_tags, _set_tags)

	@property
	def tags_items(self):
		return self._tags.iteritems()

	##########################################################################

	def encode3(self):
		return 0, self.FV3_CLASS_NAME, self.tags

	##########################################################################

	def add_item(self, item):
		if item.tags is not None and item.name is not None:
			for tag in item.tags:
				self._get_tag_list(tag).add_item(item)

	def update_item(self, item):
		self.remove_item(item)
		self.add_item(item)

	def remove_item(self, item):
		if item.name is not None:
			for tag in self._tags.itervalues():
				tag.remove_item(item)

	##########################################################################

	def _get_tag_list(self, tag):
		if tag in self._tags:
			return self._tags[tag]

		tag_obj = Tag(tag, self.catalog)
		self._tags[tag] = tag_obj
		return tag_obj


# vim: encoding=utf8: ff=unix:
