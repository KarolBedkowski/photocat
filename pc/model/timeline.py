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

__all__ = ["Timeline"]



import time

from file_image	import FileImage



class Timeline(object):
	def __init__(self, date=None, catalog=None, parent=None, level=0):
		self.date		= date
		self.catalog	= catalog
		self.tree_node	= None
		
		self.parent		= parent
		self._level		= level
		
		self.reset()


	def reset(self):
		self.dirs		= {}
		self.files		= []		


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
	def _date(self):
		if self._level < 2:
			return '%02d' % self.date
		return '%s-%02d' % (self.parent._date, self.date)

	@property
	def caption(self):
		return '%s (%d)' % (self._date, len(self.files))
		
	
	@property
	def subdirs(self):
		def items_cmp(x, y):
			return cmp(x.date, y.date)

		return sorted(self.dirs.values(), items_cmp)


	def __add_item(self, item):
		date = item.shot_date
		if date is None or date == 0:
			return
		
		self.files.append(item)
		
		if self._level == 3:
			return
		
		date = time.localtime(date)
		date_part = date[self._level]
		
		subdir = self.dirs.get(date_part)
		if subdir is None:
			subdir = Timeline(date_part, self.catalog, self, self._level+1)
			self.dirs[date_part] = subdir
		
		subdir.__add_item(item)


	def load(self):
		self.reset()
		
		if self._level != 0:
			return
		
		def add_dir(dir):
			[ self.__add_item(item) for item in dir.files ]
			[ add_dir(subdir) for subdir in dir.subdirs ]

		[ add_dir(item) for item in self.catalog.disks ]



# vim: encoding=utf8: ff=unix:

