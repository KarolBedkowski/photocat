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

import logging
_LOG = logging.getLogger(__name__)

from _element	import Element
from image		import Image


_IMAGE_FILES_EXTENSION = ('.jpg', '.png', '.gif')



class Folder(Element):

	def __init__(self, id, name, parent_id, parent=None, catalog=None, disc=None):
		Element.__init__(self, id, name, parent_id, parent, catalog)

		self.subdirs_count		= 0
		self.files_count		= 0
		self._folder_files		= None
		self._disc				= disc
		self.folder_files_offset = None
		self.folder_files_size	= None


	def init(self, parent=None, catalog=None):
		Element.init(self, parent, catalog)
		self._subdirs = []
		self._files = []


	@property
	def subdirs(self):
		return self._subdirs


	@property
	def files(self):
		return self._files


	@property
	def folder_files(self):
		if self._folder_files is None and self.folder_files_offset is not None:
			self._folder_files = eval(self._catalog.data_provider.get(self.folder_files_offset, self.folder_files_size))
		return self._folder_files or ()


	def add_folder(self, folder):
		self._subdirs.append(folder)


	def add_image(self, image):
		self._files.append(image)


	def load(self, path, options=None, on_update=None):
		_LOG.debug('Folder.load(%s)' % path)

		Element.load(self, path, options, on_update)

		subdirs = sorted(( fname for fname in os.listdir(path)
			if not fname.startswith('.') and os.path.isdir(os.path.join(path, fname))
		))

		_LOG.debug('Folder.load: len(subdirs)=%d' % len(subdirs))

		def create_subfolder(name):
			subfolder = Folder(None, name, self.id, self, self._catalog, self._disc)
			subfolder.load(os.path.join(path, name), options, on_update=on_update)
			return subfolder

		self._subdirs = map(create_subfolder, subdirs)
		self.subdirs_count = len(subdirs)
		subdirs = None

		files = sorted(( fname for fname in os.listdir(path)
			if os.path.splitext(fname)[1].lower() in _IMAGE_FILES_EXTENSION
				and not fname.startswith('.')
				and os.path.isfile(os.path.join(path, fname))
		))

		_LOG.debug('Folder.load: len(files)=%d' % len(files))

		def create_file(name):
			image = Image(None, name, self.id, self, self._catalog, self._disc)
			image.load(os.path.join(path, name), options, on_update=on_update)
			return image

		self._files = map(create_file, files)
		self.files_count = len(files)
		files = None

		self._load_caption_txt(path)
		self._load_file_folders(path)


	def update_element(self, path, options=None, on_update=None):
		_LOG.debug('Folder.update_element(%s)' % path)

		Element.update_element(self, path, options, on_update)

		subdirs = ( fname for fname in os.listdir(path)
			if not fname.startswith('.') and os.path.isdir(os.path.join(path, fname))
		)

		def create_subfolder(name):
			subfolder = [ folder for folder in self._subdirs if folder.name == name ]
			if len(subfolder) > 0:
				subfolder = subfolder[0]
				subfolder.update_element(os.path.join(path, name), options, on_update=on_update)
			else:
				subfolder = Folder(None, name, self.id, self, self._catalog, self._disc)
				subfolder.load(os.path.join(path, name), options, on_update=on_update)
			return subfolder

		self._subdirs = map(create_subfolder, subdirs)
		_LOG.debug('Folder.load: len(subdirs)=%d' % len(self._subdirs))
		self._subdirs.sort(Folder._items_cmp)
		self.subdirs_count = len(self._subdirs)
		subdirs = None

		files = ( fname for fname in os.listdir(path)
			if os.path.splitext(fname)[1].lower() in _IMAGE_FILES_EXTENSION
				and not fname.startswith('.')
				and os.path.isfile(os.path.join(path, fname))
		)

		def create_file(name):
			image = [ image for image in self._files if image.name == name ]
			if len(image) > 0:
				image = image[0]
				image.update_element(os.path.join(path, name), options, on_update=on_update)
			else:
				image = Image(None, name, self.id, self, self._catalog, self._disc)
				image.load(os.path.join(path, name), options, on_update=on_update)
			return image
		
		self._files = map(create_file, files)
		_LOG.debug('Folder.load: len(files)=%d' % len(self._files))
		self._files.sort(Folder._items_cmp)
		self.files_count = len(self._files)
		files = None
		
		self._load_caption_txt(path)
		self._load_file_folders(path)


	@staticmethod
	def _items_cmp(x, y):
		return cmp(x.name, y.name)


	def check_on_find(self, text, options=None):
		self_result = Element.check_on_find(self, text, options)
		[ self_result.extend(subdir.check_on_find(text, options)) for subdir in self._subdirs ]
		[ self_result.extend(image.check_on_find(text, options)) for image in self._files ]
		return self_result


	@property
	def folder_size(self):
		files = len(self._files)
		folders = len(self._subdirs)

		for subdir in self._subdirs:
			sfiles, sfolders = subdir.folder_size
			files += sfiles
			sfolders = sfolders

		return (files, folders)


	def _load_caption_txt(self, path):
		captions_file_path = os.path.join(path, 'captions.txt')
		if not os.path.exists(captions_file_path):
			return
		
		_LOG.debug('Folder._load_caption_txt(%s)' % captions_file_path)

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
		
		_LOG.debug('Folder._load_caption_txt_process_file(%s)' % file_name)

		if file_name == '.':
			update_obj = self
		else:
			find_update_obj = [ image for image in self._files if image.name == file_name]
			if len(find_update_obj) != 1:
				return
			update_obj = find_update_obj[0]

		if update_obj.descr is None or len(update_obj.descr) == 0:
			descr = [ file_data[key] for key in ('Title', 'Subtitle', 'Date', 'Desc') if file_data.has_key(key) ]
			update_obj.descr = '\n'.join(descr)



	def _load_file_folders(self, path):
		_LOG.debug('Folder._load_file_folders(%s)' % path)
		files = sorted(( fname for fname in os.listdir(path) if os.path.isfile(os.path.join(path, fname)) ))
		folder_files = []
		for file in files:
			file_path = os.path.join(path, file)
			size = os.path.getsize(file_path)
			date = os.path.getmtime(file_path)
			folder_files.append((file, date, size))
		self._folder_files = tuple(folder_files)

		self.folder_files_offset, self.folder_files_size = self._catalog.data_provider.append(repr(self._folder_files))




if __name__ == '__main__':
	folder = Folder(id=None, name='root', parent=None)
	folder.load('/home/k/gfx')
	print repr(folder)
	fout = file('out.yaml', 'w')
	folder.dump(fout)
	fout.close()



# vim: encoding=utf8: ff=unix:
