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

from _catalog_file	import CatalogFile
from gui			import TreeItem
from file_image		import FileImage



class Directory(CatalogFile, TreeItem):
	def __init__(self, id, name, parent, disk, *args, **kwargs):
		CatalogFile.__init__(self, id, name, parent, disk, *args, **kwargs)
		TreeItem.__init__(self)

		self.files		= []
		self.subdirs	= []


	@property
	def childs(self):
		return self.subdirs


	@property
	def childs_to_store(self):
		return self.files + self.subdirs


	@property
	def directory_size(self):
		subdirs_files = 0
		subdirs_dirs = 0
		for subdir in self.subdirs:
			dummy, dummy, subdir_files, subdir_dirs = subdir.directory_size
			subdirs_files	+= subdir_files
			subdirs_dirs	+= subdir_dirs
		return (len(self.files), len(self.subdirs), subdirs_files, subdirs_dirs)


	@property
	def directory_size_sumary(self):
		return sum(self.directory_size)


	def add_child(self, item):
		if isinstance(item, Directory):
			self.subdirs.append(item)
		else:
			self.files.append(item)


	def load(self, path, options, on_update):
		CatalogFile.load(self, path, options, on_update)
		self._load_subdirs(path, options, on_update)
		self._load_files(path, options, on_update)
		return True


	def update(self, path, options, on_update):
		CatalogFile.update(self, path, options, on_update)
		self._update_subdirs(path, options, on_update)
		self._update_files(path, options, on_update)
		return True


	def remove_subdir(self, subdir):
		self.subdirs.remove(subdir)
		self.catalog.dirty = True


	def remove_file(self, file):
		self.files.remove(file)
		self.catalog.dirty = True


	def check_on_find(self, text, options=None):
		self_result = CatalogFile.check_on_find(self, text, options)
		[ self_result.extend(subdir.check_on_find(text, options))	for subdir in self.subdirs ]
		[ self_result.extend(image.check_on_find(text, options))	for image in self.files ]
		return self_result


	def _load_subdirs(self, path, options, on_update):
		subdirs = self.__folder_subdirs_list(path)
		include_empty_subdirs = options.get('include_empty_subdirs', False)
		for subdir, subdir_path in subdirs:
			subdir_obj = Directory(id=-1, name=subdir, parent=self, disk=self.disk)
			subdir_obj.load(subdir_path, options, on_update)

			if include_empty_subdirs or subdir_obj.directory_size_sumary > 0:
				self.subdirs.append(subdir_obj)


	def _update_subdirs(self, path, options, on_update):
		include_empty_subdirs = options.get('include_empty_subdirs', False)

		new_subdirs			= []
		subdirs				= self.__folder_subdirs_list(path)
		dir_subdirs_names	= dict(( (subdir.name, subdir) for subdir in self.subdirs ))

		for subdir, subdir_path in subdirs:
			subdir_obj = dir_subdirs_names.get(subdir)
			if subdir_obj is None:
				subdir_obj = Directory(id=-1, name=subdir, parent=self, disk=self.disk)
				subdir_obj.load(subdir_path, options, on_update)
			else:
				subdir_obj.update(subdir_path, options, on_update)

			if include_empty_subdirs or subdir_obj.directory_size_sumary > 0:
				new_subdirs.append(subdir_obj)

		self.subdirs = new_subdirs


	def _load_files(self, path, options, on_update):
		files = self.__folder_files_list(path)
		for filename, file_path in files:
			fileimage = FileImage(id=-1, name=filename, parent=self, disk=self.disk)
			fileimage.load(file_path, options, on_update)
			self.files.append(fileimage)


	def _update_files(self, path, options, on_update):
		new_files	= []
		files		= self.__folder_files_list(path)
		files_dict	= dict(( (file.name, file) for file in self.files ))

		for filename, file_path in files:
			fileimage = files_dict.get(filename)
			if fileimage is None:
				fileimage = FileImage(id=-1, name=filename, parent=self, disk=self.disk)
				fileimage.load(file_path, options, on_update)
			else:
				fileimage.update(file_path, options, on_update)
			new_files.append(fileimage)

		self.files = new_files


	def __folder_files_list(self, path):
		# TODO: zoptymalizować
		files = sorted((
				( fname, os.path.join(path, fname) )
				for fname in os.listdir(path)
				if os.path.splitext(fname)[1].lower() in FileImage.IMAGE_FILES_EXTENSION
					and not fname.startswith('.')
					and os.path.isfile(os.path.join(path, fname))
		))
		return files


	def __folder_subdirs_list(self, path):
		# TODO: zoptymalizować
		subdirs = sorted((
				( fname, os.path.join(path, fname) )
				for fname in os.listdir(path)
				if not fname.startswith('.')
					and os.path.isdir(os.path.join(path, fname))
		))
		return subdirs



# vim: encoding=utf8: ff=unix:
