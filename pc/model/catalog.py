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
import os.path

import gettext
_ = gettext.gettext

from kpylibs.myobject import MyObject

from tags_provider			import Tags
from disk					import Disk
from dataprovider			import DataProvider
from _element				import BaseElement
from storage				import Storage
from catalog_state			import CatalogState



class Catalog(BaseElement):

	def __init__(self, filename):
		BaseElement.__init__(self, -1, filename, None, catalog=self)
		self._disks 		= []
		self._data_provider = DataProvider();
		self._tags_provider	= Tags()
		self._indexfilepath	= None
		self._filesdir		= None
		self._datafilepath	= None
		self._tree_node		= None
		self._state			= CatalogState()
		self.dirty			= False

		self._set_filename(filename)

		self.load()


	@property
	def data_provider(self):
		return self._data_provider


	@property
	def tags_provider(self):
		return self._tags_provider


	@property
	def filename(self):
		return self._indexfilepath


	@property
	def disks(self):
		return self._disks


	@property
	def caption(self):
		if self.dirty:
			return '%s *' % self.name
		return self.name


	@property
	def state(self):
		self._state.last_offset = self._data_provider.offset
		return self._state


	def _get_id(self):
		self._state.last_id = self._state.last_id + 1
		return self._state.last_id;

	def _set_id(self, id):
		if id > self._state.last_id:
			self._state.last_id = id

	id_provider = property(_get_id, _set_id)


	@property
	def catalog(self):
		return self


	def save_catalog(self):
		Storage.save(self._indexfilepath, self)
		self.dirty = False


	def load(self, filename=None):
		self._set_filename(filename)
		self._tags_provider.reset()
		self._disks = Storage.load(self._indexfilepath, self)
		self._after_load()
		self.data_provider.open(self._datafilepath)


	def close(self):
		self._data_provider.close()


	def add_disk(self, path, name, descr=None, options=None, on_update=None):
		disk = Disk(None, name, self.id, self)
		disk.descr = descr
		disk.load(path, options=options, on_update=on_update)
		self._disks.append(disk)
		self._data_provider.flush()
		self.dirty = True


	def del_disk(self, disk):
		self._disks.remove(disk)
		self.dirty = True


	def update_disk(self, path, disk, options=None, on_update=None, name=None, descr=None):
		disk.update_element(path, options=options, on_update=on_update)
		if name is not None:
			disk.name = name
		if descr is not None:
			disk.descr = descr
		self._data_provider.flush()
		self.dirty = True


	def _set_filename(self, filename):
		if filename is not None:
			self._indexfilepath	= filename
			self._filesdir		= os.path.dirname(filename)
			self._datafilepath	= os.path.splitext(filename)[0] + ".data"
			self.name			= os.path.basename(filename)


	def set_state(self, state):
		self._state = state
		self._data_provider.offset = state.last_offset


	def check_on_find(self, text, options=None):
		self_result = BaseElement.check_on_find(self, text, options)
		[ self_result.extend(disk.check_on_find(text, options)) for disk in self._disks ]
		return self_result


	def _after_load(self):
		self._disks.sort(lambda x,y: cmp(x.name, y.name))


	def rebuild(self):
		self._state.last_offset, saved_size = self._data_provider.rebuild(self._disks)
		self.save_catalog()
		self._data_provider.open()
		return saved_size


	@staticmethod
	def fast_count_files_dirs(path):
		_IMAGE_FILES_EXTENSION = ('.jpg', '.png', '.gif')

		def count_folder(path):
			content = [ os.path.join(path, name) 
					for name 
					in os.listdir(path) 
					if not name.startswith('.')
			]

			content_size = sum(( 1 for item 
				in content 
				if os.path.isdir(item) 
					or (os.path.isfile(item) 
						and os.path.splitext(item)[1].lower() in _IMAGE_FILES_EXTENSION 
					)
			))

			content_size += sum( ( count_folder(item) for item in content if os.path.isdir(item) ) )
			return content_size

		return count_folder(path)


	@staticmethod
	def update_images_from_image(images, master_image):
		descr = master_image.descr
		if descr == '':
			descr = None
		else:
			descr = descr.strip()

		tags = master_image.tags

		for image in images:
			if descr is not None:
				image.descr = descr
			image.set_tags(tags)


	@property
	def stat(self):
		result = []

		result.append(_('Disks: %d') % len(self._disks))

		files, folders = 0, 0
		for disk in self._disks:
			dfiles, dfolders = disk.root.folder_size
			files += dfiles
			folders += dfolders

		result.append(_('Folders: %d') % folders)
		result.append(_('Files: %d') % files)

		return result




if __name__ == '__main__':
	from pc.model.catalog import Catalog as _Catalog
	catalog = _Catalog('test.index')
	catalog.add_disk('/home/k/gfx', name='root')
	#print repr(catalog)
	#catalog.save()

	from storage import Storage
	Storage.save('test.index', catalog)

	catalog.close()

	del catalog

	#catalog = _Catalog('test.index')
	#print repr(catalog)
	#catalog.close()


# vim: encoding=utf8: ff=unix:
