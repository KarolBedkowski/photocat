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

import logging
import Queue

_LOG = logging.getLogger(__name__)

class Cache(object):
	def __init__(self, size=2000):
		_LOG.info('Cache.__init__(%d)' % size)
		self.size = size
		self._data = None
		self.clear()
	
	def __setitem__(self, key, item):
		if key in self._data:
			return
		if self._fifo.full():
			del self._data[self._fifo.get()]
		self._data[key] = item
		self._fifo.put(key)

	def __getitem__(self, key):
		return self._data[key]

	def __contains__(self, key):
		return key in self._data

	def __len__(self):
		return len(self._data)

	def get(self, key, default=None):
		return self._data.get(key, default)

	def clear(self):
		_LOG.info('Cache.clear curr_size=%d' % (len(self._data) 
				if self._data else 0))
		self._fifo = Queue.Queue(self.size)
		self._data = {}


# vim: encoding=utf8: ff=unix: 
