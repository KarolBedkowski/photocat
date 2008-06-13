#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Storage - storage.py

 KPyLibs
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

 This file is part of KPyLibs

 KPyLibs is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 SAG is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id: wnd_shell.py 5 2007-06-05 20:27:47Z k $'

__all__			= []


import logging
_LOG = logging.getLogger(__name__)

from struct import unpack, calcsize, pack



class Storage:
	def __init__(self, filename):
		self.filename = filename

		self._file = None
		
		# offsety w pliku poszczególnych bloków
		self._blocks_table = {}
		
		# lista pustych blokow (offset, size)
		self._free_blocks  = []
		
	
	def __del__(self):
		self.close()

	
	def open(self):
		if self._file is None:
			try:
				self._file = file(self.filename, 'r+b')
				self._check_file()
			except Exception, err:
				_LOG.exception('Storage.open file "%s" error' % self.filename)
				if self._file is not None:
					self._file.close()
				raise StandardError(e)


	def close(self):
		if self._file is not None:
			self._file.close()
			self._file = None


	def get(self, id):
		pass


	def put(self, id, item):
		pass


	def delete(self, id):
		pass


	def _merge_free_blocks(self):
		pass

	
	def _check_file(self):
		_LOG.debug('Storage._check_file()')
		
	

# vim: encoding=utf8:
