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
from struct import unpack, calcsize, pack

import logging
_LOG = logging.getLogger(__name__)



class DataProvider:
	_DATA_FILE_HEADER_SIZE	= 52
	_DATA_FILE_HEADER_ID	= 'PhotoCatalog_DataFile'
	_DATA_FILE_VERSION_MAX	= 2
	_DATA_BLOCK_HEADER_SIZE	= calcsize('LLL')
	_DATA_BLOCK_HEADER_PREFIX = 0x01010101


	def __init__(self, filename):
		self.next_offset	= 0
		self.filename		= os.path.splitext(filename)[0] + ".data"

		self._file					= None
		self._last_offset_file_pos	= len(self._DATA_FILE_HEADER_ID) + calcsize("I")


	def __del__(self):
		self.close()


	def get_data(self, offset_size):
		offset, size = offset_size
		_LOG.debug('DataProvider.get_data(%d, %d)' % (offset, size))
		if self._file is None:
			_LOG.warn('DataProvider.get: file closed')
			return None

		self._file.seek(offset)
	
		# naglowek
		h_prefix, h_offset, h_length = unpack('LLL', self._file.read(self._DATA_BLOCK_HEADER_SIZE))
		if h_prefix != self._DATA_BLOCK_HEADER_PREFIX or h_offset != offset or h_length != size:
			raise StandardError('Invalid block')

		return self._file.read(size)


	def put_data(self, offset, data):
		length = len(data)
		_LOG.debug('DataProvider.put_data(%d, len=%d)' % (offset, length))
		
		self.next_offset = self._write_block(self._file, offset, length, data)
		
		return (offset, length)


	def append(self, data):
		return self.put_data(self.next_offset, data)


	def open(self, force_new=False):
		_LOG.debug('DataProvider.open(%s)' % self.filename)

		self.close()

		self._file = None
		if os.path.exists(self.filename) and force_new:
			os.unlink(self.filename)

		if not force_new and os.path.exists(self.filename):
			try:
				self._file = file(self.filename, 'r+b')
				self.next_offset = self._check_file(self._file)
			except Exception, e:
				_LOG.exception('DataProvider.open(%s) error ' % self.filename)
				self.close()
				raise Exception(e)
		else:
			self._file = file(self.filename, 'w+b')
			self.next_offset = self._write_header(self._file)


	def close(self):
		if self._file is not None:
			self._file.close()
			self._file = None


	def rebuild(self, catalog):
		return
		self._file.flush()
		new_file = file(self.filename + '.tmp', 'w+b')

		new_file_next_offset = self._write_header(new_file)

		files_to_update = []
		dirs_to_update	= []

		def copy_data(offset, size, new_offset):
			data = self.get_data((offset, size))
			next_offset = self._write_block(new_file, new_offset, size, data)
			return new_offset


		#def copy_directory(dir, 




	######################################################################################


	def _check_file(self, dest_file):
		""" DataProvider._check_file(dest_file) -> int -- sprawdzenie nagłówka pliku
			@param dest_file	plik do którego są zapisywane
			@return koniec danych

			Nagłówek:
				20b - nagłówek
				int - wersja
				ulong - ostatni offset
		"""
		_LOG.debug('DataProvider._check_file()')
		header = dest_file.read(len(self._DATA_FILE_HEADER_ID))
		if header != self._DATA_FILE_HEADER_ID:
			raise IOError('Invalid file')

		# sprawdzenie wersji
		version = unpack("I", dest_file.read(calcsize("I")))[0]
		if version > self._DATA_FILE_VERSION_MAX:
			raise IOError('Invalid file version: %d (supported %d)' % (version, self._DATA_FILE_VERSION_MAX))

		# ostatni offset
		next_offset = unpack("L", dest_file.read(calcsize("L")))[0]
		_LOG.debug('DataProvider._check_file: next_offset=%d' % self.next_offset)
		return next_offset


	def _write_header(self, dest_file):
		''' DataProvider._write_header(dest_file) -> int -- zapisanie nagłówka pliku
			@param dest_file	plik do którego są zapisywane
			@return koniec nagłówka
		'''
		_LOG.debug('DataProvider._write_header()')

		dest_file.seek(0)
		dest_file.write("\x00" * self._DATA_BLOCK_HEADER_SIZE)
		dest_file.seek(0)
		dest_file.write(self._DATA_FILE_HEADER_ID)
		dest_file.write(pack("I", self._DATA_FILE_VERSION_MAX))

		next_offset = self._DATA_FILE_HEADER_SIZE
		self._write_next_offset(dest_file, next_offset)

		dest_file.seek(self._DATA_FILE_HEADER_SIZE)
		dest_file.flush()
		return next_offset


	def _write_next_offset(self, dest_file, next_offset):
		''' DataProvider._write_next_offset(dest_file, next_offset) -- zapisanie w nagłówku pliku danych o końcu danych 
			@param dest_file	plik do którego są zapisywane
			@param next_offset	koniec danych
		'''
		current_offset = dest_file.tell()
		dest_file.seek(self._last_offset_file_pos)
		dest_file.write(pack("L", next_offset))
		dest_file.seek(current_offset)


	def _write_block(self, dest_file, offset, size, data):
		'''DataProvider._write_block(dest_file, offset, size, data) -> int -- zapisanie bloku danych
			@param dest_file	plik do którego są zapisywane
			@param offset		offset początku 
			@param size			rozmiar bloku danych (bez nagłówka)
			@param data			dane do zapisania
			@return następny offset (koneic danych)
		'''
		dest_file.seek(offset)
		# nagłówek bloku
		dest_file.write(pack('LLL', self._DATA_BLOCK_HEADER_PREFIX, offset, size))
		# dane
		dest_file.write(data)
		# kolejny offset
		next_offset = self._next_offset(dest_file.tell())
		self._write_next_offset(dest_file, next_offset)
		dest_file.flush()
		return next_offset


	@staticmethod
	def _next_offset(offset):
		''' magia... '''
		return offset + 4 - (offset % 4)




# vim: encoding=utf8: ff=unix:
