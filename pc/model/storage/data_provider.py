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
from struct import unpack, calcsize, pack

import logging
_LOG = logging.getLogger(__name__)




class AbortRebuild(StandardError):
	pass



class DataProvider:
	_DATA_FILE_HEADER_SIZE	= 52
	_DATA_FILE_HEADER_ID	= 'PhotoCatalog_DataFile'
	_DATA_FILE_VERSION_MIN	= 2
	_DATA_FILE_VERSION_MAX	= 2
	_DATA_BLOCK_HEADER_SIZE	= calcsize('LLL')
	_DATA_BLOCK_HEADER_PREFIX = 0x01010101


	def __init__(self, filename):
		self.next_offset	= 0
		self.filename		= os.path.splitext(filename)[0] + ".data"
		self.objects_count	= 0

		self._file					= None
		self._last_offset_file_pos	= len(self._DATA_FILE_HEADER_ID) + calcsize("I")


	def __del__(self):
		self.close()


	def get_data(self, offset, src_file=None):
		''' DataProvider.get_data(offset_size) -> str -- pobranie danych
			@param offset_size (offset, size) danych do pobrania
			@return dane
		'''
		_LOG.debug('DataProvider.get_data(%d)' % offset)
		src_file = src_file or self._file
		if src_file is None:
			_LOG.warn('DataProvider.get: file closed')
			return None

		src_file.seek(offset)

		# naglowek
		h_prefix, h_offset, h_length = unpack('LLL', src_file.read(self._DATA_BLOCK_HEADER_SIZE))
		prefix_dont_match = h_prefix != self._DATA_BLOCK_HEADER_PREFIX
		offset_dont_match = h_offset != offset
		if prefix_dont_match or offset_dont_match:
			raise StandardError('Invalid block prefix=%r  offset=%r' %
					(prefix_dont_match, offset_dont_match)
			)

		return src_file.read(h_length)


	def append(self, data):
		''' DataProvider.append(data) -> (int, int) -- dodanie danych do pliku
			@param data dane do zapisanie
			@return (offset, size) zapisanych danych
		'''
		length = len(data)
		offset = self.next_offset
		_LOG.debug('DataProvider.put_data(%d, len=%d)' % (offset, length))

		self.next_offset = self._write_block(self._file, offset, length, data)

		return offset


	def open(self, force_new=False):
		''' DataProvider.open([force_new]) -- otwarcie pliku danych
			@param force_new wymuszenie utworzenia nowego pliku
		'''
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
				raise StandardError(e)

		else:
			self._file = file(self.filename, 'w+b')
			self.next_offset = self._write_header(self._file)


	def close(self):
		''' DataProvider.close() -- zamknięcie pliku '''
		if self._file is not None:
			self._file.close()
			self._file = None


	def rebuild(self, catalog, progress_callback=None):
		''' DataProvider.rebuild(catalog) -> int -- przebudowanie pliku danych.
			Przebudowywuje plik danych i usuwa z niego śmieci.

			@param catalog katalog do przebudowy
			@return ilość zaoszczędzonego miejsca
		'''
		self._file.flush()

		saved_space		= -1
		new_file		= None
		tmp_filename	= self.filename + '.tmp'
		old_filename	= self.filename + '.old'

		old_objects_count = self.objects_count
		self.objects_count = 0

		try:
			new_file = file(tmp_filename, 'w+b')
			new_file_next_offset = self._write_header(new_file)

			files_to_update = []

			# kopiowanie danych
			def copy_data(offset, new_offset):
				data = self.get_data(offset)
				next_offset = self._write_block(new_file, new_offset, len(data), data)
				if progress_callback:
					if not progress_callback(self.objects_count):
						raise AbortRebuild()

				return next_offset

			# kopiowanie katalogu z podkatalogami
			def copy_directory(dir, next_offset):
				for image in dir.files:
					image_thumb	= None
					image_exif	= None

					if image.thumb is not None:
						image_thumb = next_offset
						next_offset = copy_data(image.thumb, next_offset)

					if image.exif is not None:
						image_exif = next_offset
						next_offset = copy_data(image.exif, next_offset)

					files_to_update.append((image, image_thumb, image_exif))

				for subdir in dir.subdirs:
					next_offset = copy_directory(subdir, next_offset)

				return next_offset

			# kopiowanie katalogu
			next_offset = new_file_next_offset
			for disk in catalog.disks:
				next_offset = copy_directory(disk, next_offset)

			new_file.close()
			new_file = None
			self._file.close()
			self._file = None

		except AbortRebuild:
			_LOG.info('DataProvider.rebuild: abort')
			self.objects_count = old_objects_count

		except IOError, err:
			_LOG.exception('DataProvider.rebuild error')
			self.objects_count = old_objects_count
			raise StandardError(err)

		else:
			os.rename(self.filename, old_filename)
			os.rename(tmp_filename, self.filename)

			# rozmiary plików przed i po
			old_size = os.path.getsize(old_filename)
			new_size = os.path.getsize(self.filename)
			saved_space = old_size - new_size

			# aktualizacja odnośników w katalogu
			for image, image_thumb, image_exif in files_to_update:
				if image_thumb is not None:		image.thumb = image_thumb
				if image_exif is not None:		image.exif = image_exif

			# wywalenie starego pliku
			os.unlink(old_filename)

		finally:
			if new_file is not None:
				new_file.close()

			if os.path.exists(tmp_filename):
				os.unlink(tmp_filename)

			if self._file is not None:
				self._file.close()
				self._file = None

			self.open()
			catalog.dirty = True

		return saved_space


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

		# sprawdzenie nagłówka
		header = dest_file.read(len(self._DATA_FILE_HEADER_ID))
		if header != self._DATA_FILE_HEADER_ID:
			raise IOError('Invalid file')

		# sprawdzenie wersji
		version = unpack("I", dest_file.read(calcsize("I")))[0]
		if version > self._DATA_FILE_VERSION_MAX or version < self._DATA_FILE_VERSION_MIN:
			raise IOError(
				'Invalid file version: %d (supported %d-%d)' % \
					(version, self._DATA_FILE_VERSION_MIN, self._DATA_FILE_VERSION_MAX)
			)

		# ostatni offset
		next_offset = unpack("L", dest_file.read(calcsize("L")))[0]
		_LOG.debug('DataProvider._check_file: next_offset=%d' % self.next_offset)

		# liczba plikow
		self.objects_count = unpack("L", dest_file.read(calcsize("L")))[0]
		_LOG.debug('DataProvider._check_file: objects_count=%d' % self.objects_count)

		return next_offset


	def _write_header(self, dest_file):
		''' DataProvider._write_header(dest_file) -> int -- zapisanie nagłówka pliku
			@param dest_file	plik do którego są zapisywane
			@return koniec nagłówka
		'''
		_LOG.debug('DataProvider._write_header()')

		# zapisanie nagłówka
		dest_file.seek(0)
		dest_file.write("\x00" * self._DATA_BLOCK_HEADER_SIZE)
		dest_file.seek(0)
		dest_file.write(self._DATA_FILE_HEADER_ID)

		# wersji
		dest_file.write(pack("I", self._DATA_FILE_VERSION_MAX))

		# kolejny offset
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
		dest_file.seek(self._last_offset_file_pos)
		dest_file.write(pack("LL", next_offset, self.objects_count))


	def _write_block(self, dest_file, offset, size, data):
		'''DataProvider._write_block(dest_file, offset, size, data) -> int -- zapisanie bloku danych
			@param dest_file	plik do którego są zapisywane
			@param offset		offset początku
			@param size			rozmiar bloku danych (bez nagłówka)
			@param data			dane do zapisania
			@return następny offset (koneic danych)
		'''
		_LOG.debug('DataProvider._write_block(%d, %d)' % (offset, size))
		dest_file.seek(offset)
		# nagłówek bloku
		dest_file.write(pack('LLL', self._DATA_BLOCK_HEADER_PREFIX, offset, size))
		# dane
		dest_file.write(data)
		# kolejny offset
		next_offset = self._next_offset(dest_file.tell())

		self.objects_count += 1

		self._write_next_offset(dest_file, next_offset)
		return next_offset


	@staticmethod
	def _next_offset(offset):
		''' magia... '''
		return offset + 4 - (offset % 4)




# vim: encoding=utf8: ff=unix:
