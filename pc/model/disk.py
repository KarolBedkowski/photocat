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
__revision__	= '$Id$'



import time

from directory	import Directory



class Disk(Directory):
	def __init__(self, id, name, parent, catalog, *args, **kwargs):
		self.catalog		= catalog
		self.add_date		= kwargs.get('add_date')
		self.update_date	= kwargs.get('update_date')

		Directory.__init__(self, id, name, parent, self, *args, **kwargs)

	
	@property
	def path(self):
		return ''


	def load(self, path, options, on_update):
		Directory.load(self, path, options, on_update)
		self.update_date = self.add_date = time.time()
		return True


	def update(self, path, options, on_update):
		Directory.update(self, path, options, on_update)
		self.update_date = time.time()
		return True


	@classmethod
	def _attrlist(cls):
		attribs = Directory._attrlist()
		attribs.extend((('add_date', int), ('update_date', int)))
		return attribs




# vim: encoding=utf8: ff=unix:
