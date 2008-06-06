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

from gui		import TreeItem
from disk		import Disk
from storage	import DataProvider
from tag		import Tags
from timeline	import Timeline



class Catalog(TreeItem):
	def __init__(self, filename):
		TreeItem.__init__(self)

		self.catalog_filename	= filename
		self.name				= os.path.basename(filename)
		self.last_id			= None
		self.last_offset		= None
		self.dirty				= True

		self.disks				= []
		self.catalog			= self

		self.data_provider		= DataProvider(filename)
		self.tags_provider		= Tags(self)
		self.timeline			= Timeline(None, self)
		
		self.current_disks		= []


	@property
	def caption(self):
		return self.name + (self.dirty and ' *' or '')


	@property
	def childs(self):
		return self.disks


	@property
	def childs_to_store(self):
		return self.disks
	
	
	@property
	def object_in_files(self):
		def count_objects_in_dir(directory):
			return sum((image.data_objects_count for image in directory.files)) + \
					sum(( count_objects_in_dir(subdir) for subdir in directory.subdirs ))
		return sum(( count_objects_in_dir(disk) for disk in self.disks ))
	

	@property
	def dirty_objects_count(self):
		objects_count = self.data_provider.objects_count
		if objects_count == 0:
			return 0, 0
		object_in_files = self.object_in_files
		dirty = objects_count - object_in_files
		dirtyp = 100*dirty/objects_count
		return dirty, dirtyp


	##########################################################################


	def close(self):
		self.data_provider.close()


	def add_disk(self, path, name, descr, options, on_update):
		disk = Disk(id=-1, name=name, parent=None, catalog=self)
		disk.desc = descr
		disk.load(path, options, on_update=on_update)
		self.disks.append(disk)
		self.disks.sort(lambda x,y: cmp(x.name, y.name))
		self.dirty = True
		return disk


	def remove_disk(self, disk):
		if disk in self.disks:
			disk.delete()
			self.disks.remove(disk)
			self.dirty = True
			return True
		return False


	def update_disk(self, disk, path, name, descr, options, on_update):
		disk.name = name
		disk.desc = descr
		disk.update(path, options, on_update)
		self.dirty = True
		return True


	def encode(self):
		return ''


	def check_on_find(self, text, options=None):
		self_result = []
		[ self_result.extend(disk.check_on_find(text, options)) for disk in self.disks ]
		return self_result


	def fill_shot_date(self):
		[ disk.fill_shot_date() for disk in self.disks ]
		

	##########################################################################


	@staticmethod
	def fast_count_files_dirs(path):
		""" Szybkie liczenie ile jest plikow i katalogow w ścieżce (i w podkatalogach) """

		_IMAGE_FILES_EXTENSION = ('.jpg', '.png', '.gif')

		def count_folder(path):
			content = [ os.path.join(path, name)
					for name
					in os.listdir(path)
					if not name.startswith('.')
			]

			content_size = sum((
				os.path.getsize(item)
				for item in content
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
		""" Przepisanie atrybutów z jednego obiektu do drugiego.
			Przepisywane są tylko te, które nie są None.
			(Do edycji wielu plików na raz)
		"""
		desc = master_image.desc
		tags = master_image.tags
		shot_date = master_image.shot_date
		changed_tags = {}

		for image in images:
			if desc is not None:
				image.desc = desc.strip()

			if tags is not None:
				ff_changed_tags = image.set_tags(tags)
				[ changed_tags.__setitem__(key, None) for key in ff_changed_tags ]
				
			if shot_date is not None:
				image.shot_date = shot_date

		return changed_tags.keys()




# vim: encoding=utf8: ff=unix:
