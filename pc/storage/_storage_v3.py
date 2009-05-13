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



import gzip
import struct
import logging
try:
	import cPickle as pickle
except ImportError:
	import pickle

from storage_errors	import InvalidFileError, SaveFileError

from pc.model import Disk, Catalog, FileImage, Directory, Tags


_LOG = logging.getLogger(__name__)

_CLASS_NAMES = dict(( (clazz.FV3_CLASS_NAME, clazz) for clazz in (Directory, Disk, FileImage) ))
_CLASS_NAMES_TAGS = Tags.FV3_CLASS_NAME
_CLASS_NAMES_DISK = Disk.FV3_CLASS_NAME



class _ObjectFactory:
	''' Klasa generująca obiekty na podstawie wczytywanego pliku '''

	def __init__(self, catalog, objects):
		self.catalog	= catalog
		self.objects	= objects
		self.disks		= catalog.disks


	def create_object(self, oid, o_type_id, data, *argv, **kwarg):
		''' obj_factory.create_object(oid, o_type_id, data, ...) -> object -- utworzenie obiektu.
			Tworzy obiekt i dodaje go do struktury.

			@param oid			id obiektu
			@parem o_type_id	typ obiektu
			@param data			dane do zdekodowania
		'''
		if not o_type_id in _CLASS_NAMES:
			_LOG.warn('_ObjectFactory.create_object invalid class name: "%r"', o_type_id)
			return None

		klass	= _CLASS_NAMES[o_type_id]
		data	= klass.decode3(pickle.loads(data))

		data['catalog']	= self.catalog

		# wstawienie obiektow nadrzędnych
		parent = None
		if 'parent_id' in data:
			parent = self.objects.get(data['parent_id'])

		data['parent'] = parent

		disk_id = data.get('disk_id')
		if disk_id and disk_id in self.objects:
			data['disk'] = self.objects[disk_id]

		# utworzenie klasy
		self.objects[oid] = new_object = klass(oid, **data)

		if parent:
			parent.add_child(new_object)

		else:
			if o_type_id == _CLASS_NAMES_DISK:
				self.disks.append(new_object)

			else:
				_LOG.warn('id without parent oid="%d"', oid)

		return new_object



class StorageV3:
	''' Klasa statyczna do zapisywania i wczytywania katalogów v wersji 3'''

	__HEADER_HEAD = 'XYZ'
	__HEADER_HEAD_TUPLE = tuple(__HEADER_HEAD)
	__HEADER_LEN = struct.calcsize("cccLLLL")


	@staticmethod
	def save(catalog, header):
		output_file = None
		try:
			output_file = gzip.open(catalog.catalog_filename, 'w')
			output_file.write(header + '\n')

			_LOG.debug('StorageV3.save file opened, header written')

			oid, class_name, odata = catalog.tags_provider.encode3()
			tags = pickle.dumps(odata, -1)
			output_file.write(StorageV3.__pack_header(oid, class_name, len(tags)))
			output_file.write(tags)

			def write_item(item):
				oid, class_name, odata = item.encode3()
				if oid is not None:
					data = pickle.dumps(odata, -1)
					output_file.write(StorageV3.__pack_header(oid, class_name, len(data)))
					output_file.write(data)

				map(write_item, item.childs_to_store)

			write_item(catalog)

			catalog.data_provider.save()
			catalog.dirty = False

		except Exception, err:
			_LOG.exception('StorageV3.save')
			raise SaveFileError(err)

		finally:
			if output_file is not None:
				output_file.close()


	@staticmethod
	def load(input_file, catalog, objects, filename):
		oid = ''
		tags_provider = catalog.tags_provider

		obj_factory = _ObjectFactory(catalog, objects)

		while True:
			try:
				oid, o_type_id, data_len, extra_len = StorageV3.__load_header(input_file)
				if oid is None:
					break

				data = input_file.read(data_len)
				if len(data) < data_len:
					_LOG.error('truncated file data (expect: %d, have: %d)', data_len, len(data))
					raise InvalidFileError()

				data_extra = None
				if extra_len:
					data_extra = input_file.read(extra_len)
					if len(data_extra) < extra_len:
						_LOG.error('truncated file extra (expect: %d, have: %d)', extra_len, len(data_extra))
						raise InvalidFileError()

				if o_type_id == _CLASS_NAMES_TAGS:
					tags_provider.tags = pickle.loads(data)
					continue

				new_object = obj_factory.create_object(oid, o_type_id, data, data_extra)
				if new_object:
					# tagi
					tags_provider.add_item(new_object)

			except Exception,err:
				_LOG.exception('StorageV3.load(%s) oid=%d', filename, oid)
				raise InvalidFileError()


	@staticmethod
	def __pack_header(oid, o_type_id, data_len, extra_len=0):
		return struct.pack('cccLLLL', StorageV3.__HEADER_HEAD[0], StorageV3.__HEADER_HEAD[1], StorageV3.__HEADER_HEAD[2], oid, o_type_id, data_len, extra_len)


	@staticmethod
	def __load_header(input_file):
		data = input_file.read(StorageV3.__HEADER_LEN)
		if not data:
			return None, None, None, None

		if len(data) != StorageV3.__HEADER_LEN:
			_LOG.warn('file truncated header: (except: %d, load: %d)', StorageV3.__HEADER_LEN, len(data))
			raise InvalidFileError()

		h1, h2, h3, oid, o_type_id, data_len, extra_len = struct.unpack('cccLLLL', data)
		if (h1, h2, h3) != StorageV3.__HEADER_HEAD_TUPLE:
			_LOG.warn('header error: %r' % data)
			raise InvalidFileError()

		return oid, o_type_id, data_len, extra_len



# vim: encoding=utf8: ff=unix:
