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
import operator

from pc.storage.data_provider import DataProvider

from gui		import TreeItem
from disk		import Disk
from tag		import Tags
from timeline	import Timeline
from file_image	import FileImage



class Catalog(TreeItem):
	def __init__(self, filename, readonly=False):
		TreeItem.__init__(self)

		self.catalog_filename	= filename
		self.name				= os.path.basename(filename)
		self.last_id			= None
		self.last_offset		= None
		self.dirty				= True
		self.readonly 			= readonly

		self.disks				= []
		self.catalog			= self

		self.data_provider		= DataProvider(filename)
		self.tags_provider		= Tags(self)
		self.timeline			= Timeline(None, self)

		self.current_disks		= []


	@property
	def caption(self):
		return self.name + (self.dirty and ' *' or '') + (self.readonly and ' [ReadOnly]' or '')


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


	@property
	def subdirs_count(self):
		return sum(( disk.subdirs_count+1 for disk in self.disks )) # dysk tez jest katalogiem

	##########################################################################


	def close(self):
		self.data_provider.close()


	def add_disk(self, path, name, descr, options, on_update):
		if self.readonly:
			raise StandardError("read only")

		disk = Disk(-1, name, None, self)
		disk.desc = descr
		disk.load(path, options, on_update=on_update)
		self.disks.append(disk)
		self.disks.sort(key=operator.attrgetter('name'))
		self.dirty = True
		return disk


	def remove_disk(self, disk):
		if self.readonly:
			raise StandardError("read only")

		if disk in self.disks:
			disk.delete()
			self.disks.remove(disk)
			self.dirty = True
			return True

		return False


	def update_disk(self, disk, path, name, descr, options, on_update):
		if self.readonly:
			raise StandardError("read only")

		disk.name = name
		disk.desc = descr
		disk.update(path, options, on_update)
		self.dirty = True
		return True


	def encode(self):
		return ''

	def encode3(self):
		return None, None, None


	def check_on_find(self, cmpfunc, add_callback, options, progress_callback=None):
		for disk in self.disks:
			disk.check_on_find(cmpfunc, add_callback, options, progress_callback)


	def fill_shot_date(self):
		for disk in self.disks:
			disk.fill_shot_date()


	##########################################################################




# vim: encoding=utf8: ff=unix:
