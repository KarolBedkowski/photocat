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
__revision__	= '$Id: __init__.py 2 2006-12-24 21:07:13Z k $'


import os
import string

import logging
_LOG = logging.getLogger(__name__)

#import yaml

import Image as PILImage
import PngImagePlugin, JpegImagePlugin
PILImage._initialized = 2

from pc.lib import EXIF

from _element import Element
from storage_representer	import representer

_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote', 'EXIF UserComment']



class Image(Element):
	yaml_tag = '!Image'

	def __init__(self, id, name, parent_id, parent=None, catalog=None, disc=None):
		Element.__init__(self, id, name, parent_id, parent, catalog)

		self.offset = None
		self.exif	= {}
		self.thumbsize = None
		self._disc	= disc


	@property
	def index(self):
		if self._parent is None:
			return -1
		return self._parent.files.index(self)



	def load(self, path, options=None, on_update=None):
		Element.load(self, path, options, on_update)

		tmpfilename = os.tmpnam() + "_.jpg"
		
		try:
			image = PILImage.open(path)
			image.thumbnail((200, 200), PILImage.ANTIALIAS)
			image.save(tmpfilename, quality=60)
			
			self.thumbsize = os.path.getsize(tmpfilename)
			
			image = open(tmpfilename, 'rb')
			self.offset, size = self._catalog.data_provider.append(image.read(self.thumbsize))
			image.close()
		except StandardError:
			_LOG.exception('PILImage error file=%s' % path)
			
		os.unlink(tmpfilename)
		
		try:
			jpeg_file = open(path, 'rb')
			exif = EXIF.process_file(jpeg_file)
			if exif is not None:
				for key, val in ( (key, val)
						for key, val in exif.items()
						if key not in _IGNORE_EXIF_KEYS and not key.startswith('Thumbnail ')):
					val = val.printable.replace('\0', '').strip()
					val = ''.join(( zn for zn in val if zn in string.printable ))
					self.exif[key] = val
		except StandardError:
			_LOG.exception('load_exif error file=%s' % path)
		if jpeg_file is not None:
			jpeg_file.close()


	@property
	def image(self):
		if self.offset is not None:
			data = self._catalog.data_provider.get(self.offset, self.thumbsize)
			return data
		return None


	def save(self, stream):
		yaml.dump(self, stream)
		stream.write('\n---\n')
		
		
	def check_on_find(self, text, options=None):
		self_result = Element.check_on_find(self, text, options)
		# TODO: exif?
		return self_result		




#yaml.add_representer(Image, representer)

# vim: encoding=utf8: ff=unix:
