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



import os
from struct import unpack, calcsize, pack

import logging
_LOG = logging.getLogger(__name__)



_DATA_FILE_HEADER_SIZE	= 52
_DATA_FILE_HEADER_ID	= 'PhotoCatalog_DataFile'
_DATA_FILE_VERSION_MAX	= 1



class DataProvider(object):
	def __init__(self, filename=None):
		self.filename = filename
		self._file = None
		self._offset = _DATA_FILE_HEADER_SIZE
		
		_LOG.debug('DataProvider.__init__(%s)' % filename)


	def __del__(self):
		self.close()


	def _get_offset(self):
		return self._offset
	
	def _set_offset(self, offset):
		self._offset = offset
	
	offset =  property(_get_offset, _set_offset)


	def _check_file(self):
		"""
		Nagłówek:
			20b - nagłówek
			int - wersja
		"""
		_LOG.debug('DataProvider._check_file()')
		header = self._file.read(len(_DATA_FILE_HEADER_ID))
		if header != _DATA_FILE_HEADER_ID:
			raise IOError('Invalid file')
		# sprawdzenie wersji
		version = unpack("I", self._file.read(calcsize("I")))[0]
		if version > _DATA_FILE_VERSION_MAX:
			raise IOError('Invalid file version: %d (supported %d)' % (version, _DATA_FILE_VERSION_MAX))

	
	def _write_header(self, filedesc=None):
		_LOG.debug('DataProvider._write_header()')
		if filedesc is None:
			filedesc = self._file
		filedesc.seek(0)
		filedesc.write(_DATA_FILE_HEADER_ID)
		filedesc.write(pack("I", _DATA_FILE_VERSION_MAX))
		filedesc.seek(_DATA_FILE_HEADER_SIZE)
		filedesc.flush()


	def open(self, filename=None):
		if filename is not None:
			self.filename = filename
			
		_LOG.debug('DataProvider.open(%s)' % self.filename)
			
		if self.filename is not None:
			self._file = None
			if os.path.exists(self.filename):
				try:
					self._file = file(self.filename, 'r+b')
					self._check_file()
				except Exception, e:
					_LOG.exception('DataProvider.open(%s) error ' % self.filename)
					self.close()
					raise Exception(e)
			else:
				self._file = file(self.filename, 'w+b')
				self._file.write(" " * 50)
			self._write_header()


	def close(self):
		if self._file is not None:
			self._file.close()
			self._file = None


	def get(self, offset, size):
		if self._file is None:
			_LOG.warn('DataProvider.get: file closed')
		else:
			self._file.seek(offset)
			return self._file.read(size)
		return None

	
	def append(self, data):
		self._file.seek(self._offset)
		self._file.write(data)
		org_offset, self._offset = self._offset, self._next_offset(self._file.tell())
		self._file.flush()
		return (org_offset, len(data))


	def flush(self):
		if self._file is not None:
			self._file.flush()


	def rebuild(self, discs):
		if self._file is None:
			return
		self._file.flush()
		new_file = file(self.filename + '.tmp', 'w+b')
		new_file.write(" " * 50)
		self._write_header(new_file)

		opt = dict(last_offset=_DATA_FILE_HEADER_SIZE, obj_offsets=[])

		def copy_folder(folder, opt={}):
			for subdir in folder.subdirs:
				copy_folder(subdir, opt)

			for image in folder.files:
				self._file.seek(image.offset)
				data = self._file.read(image.thumbsize)

				new_offset = opt['last_offset']
				new_file.seek(new_offset)
				new_file.write(data)
				opt['last_offset'] = self._next_offset(new_file.tell())
				opt['obj_offsets'].append((image, new_offset))

		for disc in discs:
			copy_folder(disc.root, opt)

		new_file.close()
		self._file.close()
		self._file = None

		self._offset = opt['last_offset']

		os.rename(self.filename, self.filename + '.old')
		os.rename(self.filename + '.tmp', self.filename)

		for obj, offset in opt['obj_offsets']:
			obj.offset = offset

		return opt['last_offset']








	
	@staticmethod
	def _next_offset(offset):
		''' magia... '''
		return offset + (3 - (offset % 4)) + 1
	


# vim: encoding=utf8: ff=unix: 
