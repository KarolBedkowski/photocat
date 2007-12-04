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
__revision__	= '$Id: __init__.py 39 2007-11-18 15:52:57Z k $'



import os
import time

import logging
_LOG = logging.getLogger(__name__)

import gettext
_ = gettext.gettext

from kpylibs.formaters	import format_size

from storage import StorageObject



class CatalogFile(StorageObject):
	def __init__(self, id, name, parent, disk, *args, **kwargs):
		self.size = None
		self.date = None
		self.tags = None
		self.desc = None

		StorageObject.__init__(self, id, *args, **kwargs)

		self.name		= name
		self.parent		= parent
		self.disk		= disk
		self.catalog	= disk.catalog


	@property
	def caption(self):
		return str(self.name or id(self))


	def _get_info(self):
		result = []
		result.append((0, _('Name'), str(self.name)))
		if self.tags is not None and len(self.tags) > 0:
			result.append((1, _('Tags'), ', '.join(self.tags)))
		result.append((99, '', ''))
		result.append((100, _('Catalog'), self.disk.catalog.name))
		if self.disk is not None:
			result.append((101, _('Disk'), self.disk.name))
		result.append((199, '', ''))
		if self.date is not None:
			result.append((200, _('File date'), time.strftime('%c', time.localtime(self.date))))
		return result
	
	info = property(_get_info)


	@property
	def parent_id(self):
		if self.parent is None:
			return None
		return self.parent.id


	@property
	def disk_id(self):
		if self.disk is None:
			return None
		return self.disk.id


	def load(self, path, options, on_update):
		self.size = os.path.getsize(path)
		self.date = os.path.getmtime(path)
		on_update(self.name)
		return True


	def update(self, path, options, on_update):
		''' aktualizacja eleentu
			return: True=obiekt się zmienił
		'''
		old_size = self.size
		old_date = self.date
		self.size = os.path.getsize(path)
		self.date = os.path.getmtime(path)
		on_update(self.name)
		return old_size != self.size or old_date != self.date


	def set_tags(self, tags):
		self.tags = tuple(tags)
		self.disk.catalog.tags_provider.update_item(self)


	@classmethod
	def _attrlist(cls):
		attribs = StorageObject._attrlist()
		attribs.extend((
				('name', str), ('size', int), ('date', int), ('tags', tuple), 
				('desc', str), ('parent_id', int), ('disk_id', int)
		))
		return attribs






# vim: encoding=utf8: ff=unix: 
