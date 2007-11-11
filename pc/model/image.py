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
import string
import time

import gettext
_ = gettext.gettext

import logging
_LOG = logging.getLogger(__name__)

import Image as PILImage
import PngImagePlugin, JpegImagePlugin, GifImagePlugin
PILImage._initialized = 3

from pc.lib					import EXIF

from _element				import Element
from storage_representer	import representer



_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote', 'EXIF UserComment']



class Image(Element):

	def __init__(self, id, name, parent_id, parent=None, catalog=None, disc=None):
		Element.__init__(self, id, name, parent_id, parent, catalog)

		self.offset		= None
		self.exif		= {}
		self.thumbsize	= None
		self._disc		= disc
		self.dimensions = None


	@property
	def index(self):
		if self._parent is None:
			return -1
		return self._parent.files.index(self)


	def _get_main_info(self):
		result = Element._get_main_info(self)
		if self.dimensions is not None:
			result.append((_('Dimensions'), "%d x %d" % self.dimensions))
		if self.exif is not None:
			for exif_key in ('EXIF_DateTimeOriginal', 'EXIF DateTimeDigitized', 'EXIF_DateTime'):
				if self.exif.has_key(exif_key):
					try:
						ddate = time.strptime(self.exif[exif_key], '%Y:%m:%d %H:%M:%S')
						result.append((_('Date'), time.strftime('%c', ddate)))
						break
					except:
						pass


		return result

	main_info = property(_get_main_info)


	def load(self, path, options=None, on_update=None):
		Element.load(self, path, options, on_update)

		tmpfilename = os.tmpnam() + "_.jpg"

		try:
			try:
				image = PILImage.open(path)
			except:
				image =  PILImage.new('RGB', (1,1))

			if image.mode != 'RGB':
				image = image.convert('RGB')

			self.dimensions = image.size
			image.thumbnail((200, 200), PILImage.ANTIALIAS)
			image.save(tmpfilename, "JPEG", quality=50)

			self.thumbsize = os.path.getsize(tmpfilename)

			image = open(tmpfilename, 'rb')
			self.offset, size = self._catalog.data_provider.append(image.read(self.thumbsize))
			image.close()
		except StandardError:
			_LOG.exception('PILImage error file=%s' % path)

		if os.path.exists(tmpfilename):
			os.unlink(tmpfilename)

		if os.path.splitext(path)[1].lower() == '.jpg':
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
			finally:
				if jpeg_file is not None:
					jpeg_file.close()


	def update_element(self, path, options=None, on_update=None):
		if Element.update_element(self, path, options, on_update):
			self.load(path)


	@property
	def image(self):
		if self.offset is not None:
			data = self._catalog.data_provider.get(self.offset, self.thumbsize)
			return data
		return None



# vim: encoding=utf8: ff=unix:
