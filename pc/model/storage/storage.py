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



import os.path
import gzip
import time
import logging
_LOG = logging.getLogger(__name__)

from storage_errors	import LoadFileError, InvalidFileError



class Storage:
	''' Klasa statyczna do zapisywania i wczytywania katalogów '''
	def __init__(self):
		raise Exception('Static class')


	@staticmethod
	def load(filename):
		_LOG.info('Storage.load catalog=%s' % filename)
		from pc	import model

		input_file	= None
		catalog		= model.Catalog(filename)
		class_names	= {'Directory': model.Directory, 'Disk': model.Disk, 'FileImage': model.FileImage}
		objects		= {}

		try:
			input_file = gzip.open(filename)

			line = input_file.readline()
			if not Storage.__check_header(line):
				raise InvalidFileError()

			while True:
				line = input_file.readline()
				if line == '':
					break

				line = line.strip()
				if line == '' or line.startswith('#'):
					continue

				try:
					class_name, id, data = line.split("|", 2)
					id = int(id)

					if not class_names.has_key(class_name):
						_LOG.warn('invalid class name: "%s"' % line)
						continue

					klass	= class_names[class_name]
					data	= klass.decode(data)

					data['parent']	= None
					data['catalog'] = catalog

					# wstawienie obiektow nadrzędnych
					if data.has_key('parent_id'):		data['parent']	= objects.get(data['parent_id'])

					if data.has_key('disk_id'):
						disk_id = data['disk_id']
						if objects.has_key(disk_id):
							data['disk']	= objects.get(disk_id)

					# utworzenie klasy
					objects[id] = new_object = klass(id, **data)

					if data.get('parent') is None:
						if class_name == 'Disk':
							catalog.disks.append(new_object)
					else:
						data['parent'].add_child(new_object)

					# tagi
					catalog.tags_provider.add_item(new_object)

				except:
					_LOG.exception('Storage.load(%s) line="%s"' % (filename, line))
					raise InvalidFileError()

			catalog.disks.sort(lambda x,y: cmp(x.name, y.name))
			catalog.dirty = False

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

		_LOG.info('Storage.load finished')
		return catalog


	@staticmethod
	def save(catalog):
		_LOG.info('Storage.save catalog=%s' % catalog.catalog_filename)
		output_file = None
		try:
			output_file = gzip.open(catalog.catalog_filename, 'w')
			output_file.write(Storage.__get_header() + '\n')

			_LOG.debug('Storage.save file opened, header written')

			def write_item(item):
				output_file.write(item.encode() + "\n")
				map(write_item, item.childs_to_store)

			write_item(catalog)

			catalog.dirty = False

		except Exception, err:
			_LOG.exception('Storage.save')
			raise SaveFileError(err)

		finally:
			if output_file is not None:
				output_file.close()

		_LOG.info('Storage.save catalog finished')


	######################################################


	@staticmethod
	def __check_header(line):
		try:
			header, version, date = line.split('|')
			version = int(version)
			return header == 'PhotoCatalog_IndexFile' and version <= 1
		except:
			_LOG.exception('Storage.__check_header line = "%s"' % line)
		return False


	@staticmethod
	def __get_header():
		header	= 'PhotoCatalog_IndexFile'
		version	= 1
		date	= time.asctime()
		return "|".join((header, str(version), date))



# vim: encoding=utf8: ff=unix:
