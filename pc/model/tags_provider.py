# -*- coding: utf-8 -*-

"""
 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004-2007

 This file is part of Photo Catalog

 PC is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 PC is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2007'
__revision__	= '$Id$'



from image import Image


class Tag(object):
	def __init__(self, name=None, catalog=None):
		self.name		= name
		self.tree_node	= None
		self.items		= []
		self.items_files = []
		self.catalog	= catalog


	@property
	def size(self):
		return len(self.items)


	@property
	def size_files(self):
		return len(self.items_files)


	@property
	def caption(self):
		return '%s (%d/%d)' % (self.name, len(self.items_files), len(self.items))


	def remove_item(self, item):
		if isinstance(item, Image):
			if item in self.items_files:
				self.items_files.remove(item)
			return
		if item in self.items:
			self.items.remove(item)

	
	def add_item(self, item):
		if isinstance(item, Image):
			self.items_files.append(item)
			return
		self.items.append(item)




class Tags(object):
	def __init__(self, catalog=None):
		self.reset()
		self.catalog = catalog


	def reset(self):
		self._tags = {}


	def _get_tags(self):
		return self._tags.keys()

	def _set_tags(self, tag):
		if not self._tags.has_key(tag):
			self._tags[tag] = Tag(tag, self.catalog)

	tags = property(_get_tags, _set_tags)


	@property
	def tags_items(self):
		return self._tags.iteritems()


	def add_item(self, tags, item):
		for tag in tags:
			tag_list = self._get_tag_list(tag)
			tag_list.add_item(item)


	def update_item(self, tags, item, do_remove=True):
		if do_remove:
			self.remove_item(item)
		[ self._get_tag_list(tag).add_item(item) for tag in tags ]


	def remove_item(self, item):
		[ tag.items.remove_item(item) for tag in self._tags.itervalues() if item in tag.items ]


	def _get_tag_list(self, tag):
		if self._tags.has_key(tag):
			return self._tags[tag]
		self._tags[tag] = Tag(tag, self.catalog)
		return self._tags[tag]


	def get_tag(self, tag):
		return self._tags.get(tag)



# vim: encoding=utf8: ff=unix: 

