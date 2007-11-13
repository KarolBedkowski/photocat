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


import os
import time

import logging
_LOG = logging.getLogger(__name__)

import gettext
_ = gettext.gettext

from kpylibs.myobject	import MyObject
from kpylibs.formaters	import format_size



class BaseElement(MyObject):
	def __init__(self, id, name, parent_id, parent=None, catalog=None):
		self.id			= id
		self.name		= name
		self.parent_id	= parent_id
		self.tags		= tuple()
		self.descr		= None
		self.date		= None
		
		self.init(parent, catalog)


	def init(self, parent=None, catalog=None):
		''' obj.init([parent, ] [catalog]) -- inicjacja zmiennych prywatnych '''
		self._tree_node	= None
		self._parent	= parent
		self._catalog	= catalog


	@property
	def parent(self):
		''' obj.parent -> obj -- pobranie elementu nadrzednego '''

		return self._parent


	@property
	def catalog(self):
		''' obj.catalog -> Catalog() -- pobranie katalogu '''
		return self._catalog


	@property
	def path(self):
		''' obj.path -> string -- scieżka na dysku do pliku '''
		if self._parent is None:
			return self.name
		return os.path.join(self._parent.path, self.name)


	def _get_tree_node(self):
		return self._tree_node

	def _set_tree_node(self, node):
		self._tree_node = node

	tree_node = property(_get_tree_node, _set_tree_node)


	def _get_main_info(self):
		result = []
		result.append((_('Name'), str(self.name)))
		if self.date is not None:
			result.append((_('File date'), time.strftime('%c', time.localtime(self.date))))
		if self.tags is not None and len(self.tags) > 0:
			result.append((_('Tags'), ', '.join(self.tags)))
		return result

	main_info = property(_get_main_info)


	def set_tags(self, tags=None, do_remove=True):
		''' obj.set_tags([tags], [do_remove]) -- update/set tagów
		'''
		if tags is not None:
			self.tags = tuple(tags)
		else:
			self.tags = self.tags or tuple()
		if self.name is not None: # fake object
			self._catalog.tags_provider.update_item(self.tags, self, do_remove)


	def check_on_find(self, text, options=None):
		''' obj.check_on_find(text, [options]) -> [] -- lista obiektów spełniających kryteria wyszukiwania '''
		if self.descr is not None and self.descr.lower().count(text) > 0:
			return [self]
		if self.name is not None and self.name.lower().count(text) > 0:
			return [self]
		if text in self.tags:
			return [self]
		return list()




class Element(BaseElement):

	def __init__(self, id, name, parent_id, parent=None, catalog=None):
		BaseElement.__init__(self, id, name, parent_id, parent, catalog)
		self.size = None


	def init(self, parent=None, catalog=None):
		BaseElement.init(self, parent, catalog)

		if self.id is None and catalog is not None:
			self.id = catalog.id_provider


	def _get_main_info(self):
		result = BaseElement._get_main_info(self)
		if self.size is not None:
			result.append((_('Size'), format_size(self.size, True, separate=True)))
		return result
	
	main_info = property(_get_main_info)


	@property
	def disc(self):
		''' obj.disc -> Disc() -- dysk do ktorego nalezy obiekt '''
		obj = self
		while obj.parent is not None:
			obj = obj.parent
		return obj


	def load(self, path, options=None, on_update=None):
		_LOG.debug(self.__class__.__name__+".load(%s)" % path)
		if on_update is not None:
			on_update(path)
		self.size = os.path.getsize(path)
		self.date = os.path.getmtime(path)


	def update_element(self, path, options=None, on_update=None):
		_LOG.debug(self.__class__.__name__+".update_element(%s)" % path)
		if on_update is not None:
			on_update(path)
		old_size, old_date = self.size, self.date
		self.size = os.path.getsize(path)
		self.date = os.path.getmtime(path)
		return old_size != self.size or old_date != self.date




# vim: encoding=utf8: ff=unix:
