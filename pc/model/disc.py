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



if __name__ == '__main__':
	import sys
	sys.path.append('../../')

import os
import time

import logging
_LOG = logging.getLogger(__name__)

from directory		import Directory
from _idprovider 	import IdProvider
from _element		import Element



class Disc(Element):

	def __init__(self, id, name, parent_id, parent=None):
		Element.__init__(self, id, name, -1, None, catalog=parent)


	def init(self, parent=None, catalog=None):
		Element.init(self, parent, catalog)
		self._root = None


	@property
	def root(self):
		return self._root


	def add_folder(self, folder):
		self._root = folder


	def load(self, path, options=None, on_update=None):
		self._root = Directory(None, '/', self.id, self, catalog=self._catalog, disc=self)
		self._root.load(path, options=options, on_update=on_update)
		self.date = time.time()


	def update_element(self, path, options=None, on_update=None):
		self._root.update_element(path, options, on_update)
		self.date = time.time()


	def check_on_find(self, text, options=None):
		self_result = Element.check_on_find(self, text, options)
		self_result.extend(self._root.check_on_find(text, options))
		return self_result


	@property
	def path(self):
		return ''




if __name__ == '__main__':
	#from catalog import Catalog
	#catalog = Catalog()
	#disc = Disc(id=None, name='root', catalog=catalog)
	#disc.load('/home/k/gfx')
	#print repr(disc)
	#fout = file('out.yaml', 'w')
	#disc.dump(fout)
	#fout.close()
	pass


# vim: encoding=utf8: ff=unix:
