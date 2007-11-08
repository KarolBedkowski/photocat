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
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id: __init__.py 2 2006-12-24 21:07:13Z k $'



class Tags(object):
	def __init__(self):
		self.reset()


	def reset(self):
		self._tags = {}


	def _get_tags(self):
		return self._tags.keys()

	def _set_tags(self, tag):
		if not self._tags.has_key(tag):
			self._tags[tag] = []

	tags = property(_get_tags, _set_tags)


	def add_item(self, tags, item):
		for tag in tags:
			tag_list = self._get_tag_list(tag)
			if tag_list.count(item) == 0:
				tag_list.append(item)


	def update_item(self, tags, item):
		self.remove_item(item)
		[ self._get_tag_list(tag).append(item) for tag in tags ]


	def remove_item(self, item):
		[ tag_list.remove(item) for tag_list in self._tags.itervalues() if tag_list.count(item) > 0 ]



	def _get_tag_list(self, tag):
		if self._tags.has_key(tag):
			return self._tags[tag]
		self._tags[tag] = list()
		return self._tags[tag]


# vim: encoding=utf8: ff=unix: 

