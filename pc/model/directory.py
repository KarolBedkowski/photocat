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
import logging
_LOG = logging.getLogger(__name__)

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
			files, dirs, subdir_files, subdir_dirs = subdir.directory_size
			subdirs_files	+= subdir_files + files
			subdirs_dirs	+= subdir_dirs + dirs
		return (len(self.files), len(self.subdirs), subdirs_files, subdirs_dirs)


	@property
	def directory_size_sumary(self):
		return sum(self.directory_size)


	def delete(self):
		''' metoda uruchamiana przy usuwaniu obiektu '''
		CatalogFile.delete(self)
		[ sfile.delete() for sfile in self.files ]
		[ subdir.delete() for subdir in self.subdirs ]


	def add_child(self, item):
		if isinstance(item, Directory):
			self.subdirs.append(item)
		else:
			self.files.append(item)


	def load(self, path, options, on_update):
		_LOG.debug('Directory.load(%s)' % path)
		if CatalogFile.load(self, path, options, on_update):
			if not self._load_subdirs(path, options, on_update):	return False
			if not self._load_files(path, options, on_update):	 	return False

			if options.get('load_captions_txt', True):
				self._load_caption_txt(path)

			return True
		return False


	def update(self, path, options, on_update):
		_LOG.debug('Directory.update(%s)' % path)
		if CatalogFile.update(self, path, options, on_update)[1]:
			if not self._update_subdirs(path, options, on_update):	return False
			if not self._update_files(path, options, on_update):	return False

			if options.get('load_captions_txt', True):
				self._load_caption_txt(path)

			return True
		return False


	def remove_subdir(self, subdir):
		subdir.delete()
		self.subdirs.remove(subdir)
		self.catalog.dirty = True


	def remove_file(self, file):
		file.delete()
		self.files.remove(file)
		self.catalog.dirty = True


	def check_on_find(self, text, options=None):
		self_result = CatalogFile.check_on_find(self, text, options)
		[ self_result.extend(subdir.check_on_find(text, options))	for subdir in self.subdirs ]
		[ self_result.extend(image.check_on_find(text, options))	for image in self.files ]
		return self_result


	def _load_subdirs(self, path, options, on_update):
		subdirs					= self.__folder_subdirs_list(path)
		include_empty_subdirs	= options.get('include_empty_subdirs', False)
		skip_dirs_list			= options.get('skip_dirs_list', [])

		for subdir, subdir_path in subdirs:
			if subdir in skip_dirs_list:
				continue

			subdir_obj = Directory(id=-1, name=subdir, parent=self, disk=self.disk)
			if not subdir_obj.load(subdir_path, options, on_update):
				return False

			if include_empty_subdirs or subdir_obj.directory_size_sumary > 0:
				self.subdirs.append(subdir_obj)

		return True


	def _update_subdirs(self, path, options, on_update):
		include_empty_subdirs = options.get('include_empty_subdirs', False)

		new_subdirs			= []
		subdirs				= self.__folder_subdirs_list(path)
		dir_subdirs_names	= dict(( (subdir.name, subdir) for subdir in self.subdirs ))
		skip_dirs_list		= options.get('skip_dirs_list', [])

		for subdir, subdir_path in subdirs:
			subdir_obj = dir_subdirs_names.get(subdir)
			if subdir_obj is None:
				if subdir in skip_dirs_list:
					continue
				subdir_obj = Directory(id=-1, name=subdir, parent=self, disk=self.disk)
				if not subdir_obj.load(subdir_path, options, on_update):
					return False
			else:
				if not subdir_obj.update(subdir_path, options, on_update):
					return False

			if include_empty_subdirs or subdir_obj.directory_size_sumary > 0:
				new_subdirs.append(subdir_obj)

		self.subdirs = new_subdirs
		return True


	def _load_files(self, path, options, on_update):
		files = self.__folder_files_list(path)
		for filename, file_path in files:
			fileimage = FileImage(id=-1, name=filename, parent=self, disk=self.disk)
			if not fileimage.load(file_path, options, on_update):
				return False
			self.files.append(fileimage)
		return True


	def _update_files(self, path, options, on_update):
		new_files	= []
		files		= self.__folder_files_list(path)
		files_dict	= dict(( (file.name, file) for file in self.files ))

		for filename, file_path in files:
			fileimage = files_dict.get(filename)
			if fileimage is None:
				fileimage = FileImage(id=-1, name=filename, parent=self, disk=self.disk)
				if not fileimage.load(file_path, options, on_update):
					return False
			else:
				if not fileimage.update(file_path, options, on_update):
					return False
			new_files.append(fileimage)

		self.files = new_files
		return True


	def __folder_files_list(self, path):
		files_path = ( 
				(fname, os.path.join(path, fname)) 
				for fname in os.listdir(path) 
				if not fname.startswith('.') 
					and os.path.splitext(fname)[1].lower() in FileImage.IMAGE_FILES_EXTENSION
		)

		files = sorted((
				( fname, fpath )
				for fname, fpath in files_path
				if os.path.isfile(fpath)
		))
		return files


	def __folder_subdirs_list(self, path):
		files_path = ( 
				(fname, os.path.join(path, fname)) 
				for fname in os.listdir(path) 
				if not fname.startswith('.') 
		)

		subdirs = sorted((
				( fname, fpath )
				for fname, fpath in files_path
				if  os.path.isdir(fpath)
		))
		return subdirs


	def _load_caption_txt(self, path):
		captions_file_path = os.path.join(path, 'captions.txt')
		if not os.path.exists(captions_file_path):
			return

		_LOG.debug('Directory._load_caption_txt(%s)' % captions_file_path)

		captions_file = open(captions_file_path, 'r')
		current_file_name = None
		current_file_data = {}
		while True:
			line = captions_file.readline()
			if line == '':					break

			line = line.strip()

			if line.startswith('#'):		continue

			if current_file_name is None:
				if line != '':
					current_file_name = line
			elif line == '':
				self._load_caption_txt_process_file(current_file_name, current_file_data)
				current_file_data = {}
				current_file_name = None
			else:
				key, dummy, val = line.partition('=')
				if key in ('Title', 'Subtitle', 'Date', 'Desc') and len(val.strip()) > 0:
					current_file_data[key] = val

		if current_file_name != None:
			self._load_caption_txt_process_file(current_file_name, current_file_data)

		captions_file.close()


	def _load_caption_txt_process_file(self, file_name, file_data):
		if len(file_data) == 0:
			return

		_LOG.debug('Directory._load_caption_txt_process_file(%s)' % file_name)

		if file_name == '.':
			update_obj = self
		else:
			find_update_obj = [ image for image in self.files if image.name == file_name]
			if len(find_update_obj) != 1:
				return
			update_obj = find_update_obj[0]

		if update_obj.desc is None or len(update_obj.desc) == 0:
			desc = ( file_data[key] for key in ('Title', 'Subtitle', 'Date', 'Desc') if file_data.has_key(key) )
			update_obj.desc = '\n'.join(desc)



# vim: encoding=utf8: ff=unix:
