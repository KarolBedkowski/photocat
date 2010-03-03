# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


import gzip
import time
import operator
import logging

from photocat.model import Disk, Catalog, FileImage, Directory

from photocat.storage.storage_errors import LoadFileError, InvalidFileError, \
	SaveFileError
from photocat.storage._storage_v3 import StorageV3

_LOG = logging.getLogger(__name__)


class Storage:
	''' Klasa statyczna do zapisywania i wczytywania katalogów '''

	SUPPORTED_FILE_VERSION_MAX = 3
	SUPPORTED_FILE_VERSION_MIN = 1

	def __init__(self):
		raise Exception('Static class')

	@staticmethod
	def load(filename):
		_LOG.info('Storage.load catalog=%s', filename)

		input_file = None
		catalog = Catalog(filename)
		objects = {}

		time_start = time.time()

		try:
			input_file = gzip.open(filename)

			line = input_file.readline()
			fileok, version = Storage.__check_header(line)
			if not fileok:
				raise InvalidFileError()

			_LOG.info('Storage.load fileversion: %d (%s)', version, line)
			if version == 3:
				StorageV3.load(input_file, catalog, objects, filename)

			else:
				Storage.__load_v2(input_file, catalog, objects, filename)

			catalog.disks.sort(key=operator.attrgetter('name'))
			catalog.dirty = version != Storage.SUPPORTED_FILE_VERSION_MAX

			_LOG.debug('Storage.load catalog=%s  objects_in_files=%d', filename,
					catalog.object_in_files)

		except InvalidFileError, err:
			_LOG.exception('Storage.load invalid file')
			raise LoadFileError(err)

		except Exception, err:
			_LOG.exception('Storage.load error')
			catalog = None
			raise LoadFileError(err)

		finally:
			if input_file is not None:
				input_file.close()

		_LOG.info('Storage.load finished in %0.2f sec', (time.time() - time_start))
		return catalog

	@staticmethod
	def save(catalog):
		_LOG.info('Storage.save catalog=%s', catalog.catalog_filename)
		time_start = time.time()

		StorageV3.save(catalog, Storage.__get_header())

		_LOG.info('Storage.save catalog finished in %0.2f sec',
				(time.time() - time_start))

	######################################################

	@staticmethod
	def __check_header(line):
		try:
			header, version, _date = line.split('|')
			version = int(version)
			return (header == 'PhotoCatalog_IndexFile'
					and version >= Storage.SUPPORTED_FILE_VERSION_MIN
					and version <= Storage.SUPPORTED_FILE_VERSION_MAX), version

		except:
			_LOG.exception('Storage.__check_header line = "%s"', line)

		return False, None

	@staticmethod
	def __get_header():
		header = 'PhotoCatalog_IndexFile'
		version = Storage.SUPPORTED_FILE_VERSION_MAX
		date = time.asctime()
		return "|".join((header, str(version), date))

	@staticmethod
	def __save_v2(catalog):
		output_file = None
		try:
			output_file = gzip.open(catalog.catalog_filename, 'w')
			output_file.write(Storage.__get_header() + '\n')
			output_file.write('TAGS|0|%r' % catalog.tags_provider.tags)

			_LOG.debug('Storage.save file opened, header written')

			def write_item(item):
				output_file.write(item.encode() + "\n")
				for child in item.childs_to_store:
					write_item(child)

			write_item(catalog)
			catalog.data_provider.save()
			catalog.dirty = False

		except Exception, err:
			_LOG.exception('Storage.save')
			raise SaveFileError(err)

		finally:
			if output_file is not None:
				output_file.close()

	@staticmethod
	def __load_v2(input_file, catalog, objects, filename):
		class_names = {'Directory': Directory, 'Disk': Disk,
				'FileImage': FileImage}

		while True:
			line = input_file.readline()
			if line == '':
				break
			line = line.strip()
			if line == '' or line.startswith('#'):
				continue

			try:
				class_name, oid, data = line.split("|", 2)
				oid = int(oid)

				if class_name == 'TAGS':
					catalog.tags_provider.tags = eval(data)
					continue
				if not class_name in class_names:
					_LOG.warn('invalid class name: "%s"', line)
					continue

				klass = class_names[class_name]
				data = klass.decode(data)
				data['parent'] = None
				data['catalog'] = catalog

				# wstawienie obiektow nadrzędnych
				if 'parent_id' in data:
					data['parent'] = objects.get(data['parent_id'])

				if 'disk_id' in data:
					disk_id = data['disk_id']
					if disk_id in objects:
						data['disk'] = objects.get(disk_id)

					elif class_name != 'Disk':
						_LOG.warn("no disk id=%d line='%s'", disk_id, line)

				# utworzenie klasy
				objects[oid] = new_object = klass(oid, **data)

				if data.get('parent') is None:
					if class_name == 'Disk':
						catalog.disks.append(new_object)
					else:
						_LOG.warn('id without parent "%s"', line)
				else:
					data['parent'].add_child(new_object)

				# tagi
				catalog.tags_provider.add_item(new_object)

			except:
				_LOG.exception('Storage.load(%s) line="%s"', filename, line)
				raise InvalidFileError()

# vim: encoding=utf8: ff=unix:
