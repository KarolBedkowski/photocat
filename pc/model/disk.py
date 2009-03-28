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
import logging
_LOG = logging.getLogger(__name__)

import wx

from directory	import Directory

_ = wx.GetTranslation



class Disk(Directory):
	def __init__(self, oid, name, parent, catalog, *args, **kwargs):
		self.catalog		= catalog
		self.add_date		= kwargs.get('add_date')
		self.update_date	= kwargs.get('update_date')
		self.last_path		= None

		Directory.__init__(self, oid, name, parent, self, *args, **kwargs)


	@property
	def path(self):
		return ''


	def _get_info(self):
		result = Directory._get_info(self)
		result.append((150, '', ''))
		result.append((151, _('Disk added'), time.strftime('%c', time.localtime(self.add_date))))
		result.append((152, _('Disk updated'), time.strftime('%c', time.localtime(self.update_date))))
		return result

	info = property(_get_info)
	
	
	##########################################################################


	def load(self, path, options, on_update):
		Directory.load(self, path, options, on_update)
		self.update_date = self.add_date = time.time()
		self.last_path = path
		return True


	def update(self, path, options, on_update):
		Directory.update(self, path, options, on_update)
		self.update_date = time.time()
		self.last_path = path
		return True

	
	##########################################################################


	@classmethod
	def _attrlist(cls):
		attribs = Directory._attrlist()
		attribs.extend((('add_date', int), ('update_date', int), ('last_path', str)))
		return attribs




# vim: encoding=utf8: ff=unix:
