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
__revision__	= '$Id: tags_provider.py 42 2007-11-22 16:44:59Z k $'



from file_image	import FileImage



class Tag(object):
	def __init__(self, name=None, catalog=None):
		self.name		= name
		self.files		= []
		self.dirs		= []
		self.catalog	= catalog


	@property
	def files_count(self):
		return len(self.files)


	@property
	def dirs_count(self):
		return len(self.dirs)


	@property
	def caption(self):
		return '%s (%d/%d)' % (self.name, len(self.files), len(self.dirs))


	def remove_item(self, item):
		if isinstance(item, FileImage):
			if item in self.files:
				self.files.remove(item)
			return
		if item in self.dirs:
			self.dirs.remove(item)


	def add_item(self, item):
		if isinstance(item, FileImage):
			self.files.append(item)
			return
		self.dirs.append(item)




class Tags(object):
	def __init__(self, catalog):
		self.reset()
		self._catalog = catalog


	def reset(self):
		self._tags = {}


	@property
	def tags(self):
		return self._tags.keys()


	@property
	def tags_items(self):
		return self._tags.iteritems()


	def add_item(self, item):
		if item.tags is not None:
			[ self._get_tag_list(tag).add_item(item) for tag in item.tags ]


	def update_item(self, item):
		self.remove_item(item)
		self.add_item(item)


	def remove_item(self, item):
		[ tag.remove_item(item) for tag in self._tags.itervalues() ]


	def _get_tag_list(self, tag):
		if self._tags.has_key(tag):
			return self._tags[tag]
		tag_obj = Tag(tag, self._catalog)
		self._tags[tag] = tag_obj
		return tag_obj


# vim: encoding=utf8: ff=unix:

