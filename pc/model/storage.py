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
import logging
_LOG = logging.getLogger(__name__)
from struct			import pack, unpack, calcsize

from disc			import Disc
from directory		import Directory
from image			import Image
from catalog_state	import CatalogState



class Storage:

	@classmethod
	def save_v1(cls, catalog_file_path, catalog):
		outfile = gzip.open(catalog_file_path, "w")

		format = repr(catalog.dict)
		outfile.write('!catalog:')
		outfile.write(format)
		outfile.write('\n')

		outfile.write('!catalogstate:')
		outfile.write(repr(catalog.state.dict))
		outfile.write('\n')

		for disc in catalog.discs:
			outfile.write('!disc:')
			outfile.write(repr(disc.dict))
			outfile.write('\n')

			def write(folder):
				outfile.write('!folder:')
				outfile.write(repr(folder.dict_not_none))
				outfile.write('\n')

				[ write(subfold) for subfold in folder.subdirs ]

				def write_img(image):
					outfile.write('!image:')
					outfile.write(repr(image.dict_not_none))
					outfile.write('\n')

				[ write_img(image) for image in folder.files ]

			write(disc.root)

		outfile.close()


	@classmethod
	def save_v2(cls, catalog_file_path, catalog):
		outfile = gzip.open(catalog_file_path, "wb")

		def write(data):
			size = len(data)
			outfile.write(pack('L', size))
			outfile.write(data)

		write('!catalog:' + repr(catalog.dict))

		write('!catalogstate:' + repr(catalog.state.dict))

		for disc in catalog.discs:
			write('!disc:' + repr(disc.dict))

			def write_folder(folder):
				write('!folder:' + repr(folder.dict_not_none))

				[ write_folder(subfold) for subfold in folder.subdirs ]

				def write_img(image):
					write('!image:' + repr(image.dict_not_none))

				[ write_img(image) for image in folder.files ]

			write_folder(disc.root)

		outfile.close()


	save = save_v1



	@classmethod
	def load_v1(cls, catalog_file_path, catalog):
		discs	= []
		ids		= {}

		if os.path.exists(catalog_file_path):
			infile = gzip.open(catalog_file_path, "r")
			while True:
				line = infile.readline()
				if line == '':
					break

				try:
					object_name, attrs = line.split(':', 1)
					attrs = eval(attrs)
				except:
					_LOG.warn('Loading error; row=' + line)
				else:
					if object_name == '!disc':
						node = Disc(None, None, None, parent=catalog)
						node.attributes_update_fast(attrs)
						ids[node.id] = node
						discs.append(node)
					elif object_name == '!folder':
						node = Directory(None, None, None)
						node.attributes_update_fast(attrs)
						parent = ids[node.parent_id]
						ids[node.id] = node
						node.init(parent, catalog)
						node.set_tags(do_remove=False)
						parent.add_folder(node)
					elif object_name == '!image':
						node = Image(None, None, None)
						node.attributes_update_fast(attrs)
						parent = ids[node.parent_id]
						ids[node.id] = node
						node.init(parent, catalog)
						node.set_tags(do_remove=False)
						parent.add_image(node)
					elif object_name == '!catalogstate':
						node = CatalogState()
						node.attributes_update_fast(attrs)
						catalog.set_state(node)
					elif object_name == '!catalog':
						pass
					else:
						_LOG.warn('Loader.load() invalid object type: %s' % line)

			infile.close()

		return discs


	@classmethod
	def load_v2(cls, catalog_file_path, catalog):
		discs	= []
		ids		= {}

		long_len = calcsize('L')

		if os.path.exists(catalog_file_path):
			infile = gzip.open(catalog_file_path, "rb")
			while True:
				size_str = infile.read(long_len)
				if size_str == '':
					break

				size = unpack('L', size_str)[0]
				line = infile.read(size)

				try:
					object_name, attrs = line.split(':', 1)
					attrs = eval(attrs)
				except:
					_LOG.warn('Loading error; row=' + line)
				else:
					if object_name == '!disc':
						node = Disc(None, None, None, parent=catalog)
						node.attributes_update_fast(attrs)
						ids[node.id] = node
						discs.append(node)
					elif object_name == '!folder':
						node = Directory(None, None, None)
						node.attributes_update_fast(attrs)
						parent = ids[node.parent_id]
						ids[node.id] = node
						node.init(parent, catalog)
						node.set_tags(do_remove=False)
						parent.add_folder(node)
					elif object_name == '!image':
						node = Image(None, None, None)
						node.attributes_update_fast(attrs)
						parent = ids[node.parent_id]
						ids[node.id] = node
						node.init(parent, catalog)
						node.set_tags(do_remove=False)
						parent.add_image(node)
					elif object_name == '!catalogstate':
						node = CatalogState()
						node.attributes_update_fast(attrs)
						catalog.set_state(node)
					elif object_name == '!catalog':
						pass
					else:
						_LOG.warn('Loader.load() invalid object type: %s' % line)

			infile.close()

		return discs


	load = load_v1


# vim: encoding=utf8: ff=unix: 
