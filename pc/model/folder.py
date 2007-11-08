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

#import yaml

from _element	import Element
from image		import Image
from storage_representer	import representer



class Folder(Element):
	yaml_tag = '!Folder'

	def __init__(self, id, name, parent_id, parent=None, catalog=None, disc=None):
		Element.__init__(self, id, name, parent_id, parent, catalog)
		
		self.subdirs_count = 0
		self.files_count = 0

		self._disc = disc
		
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
			if fname.lower().endswith('.jpg') and not fname.startswith('.')
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


	def on_restore(self, catalog, disc):
		Element.on_restore(self, catalog, disc)
		
		[ subdir.on_restore(catalog, disc) for subdir in self.subdirs ]
		[ image.on_restore(catalog, disc) for image in self.files ]


	def save(self, stream):
		yaml.dump(self, stream)
		stream.write('\n---\n')
		[ subdir.save(stream) for subdir in self._subdirs ]
		[ image.save(stream) for image in self._files ]


	def check_on_find(self, text, options=None):
		self_result = Element.check_on_find(self, text, options)
		[ self_result.extend(subdir.check_on_find(text, options)) for subdir in self._subdirs ]
		[ self_result.extend(image.check_on_find(text, options)) for image in self._files ]
		return self_result


#yaml.add_representer(Folder, representer)



if __name__ == '__main__':
	folder = Folder(id=None, name='root', parent=None)
	folder.load('/home/k/gfx')
	print repr(folder)
	fout = file('out.yaml', 'w')
	folder.dump(fout)
	fout.close()



# vim: encoding=utf8: ff=unix: 
