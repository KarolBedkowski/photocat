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
__revision__	= '$Id: __init__.py 39 2007-11-18 15:52:57Z k $'


import os
import string
import time
import logging
_LOG = logging.getLogger(__name__)

import gettext
_ = gettext.gettext

import Image as PILImage
import PngImagePlugin, JpegImagePlugin, GifImagePlugin
PILImage._initialized = 3
from PIL.ExifTags import TAGS

from _catalog_file			import CatalogFile



_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote'] # 'EXIF UserComment']



class FileImage(CatalogFile):

	IMAGE_FILES_EXTENSION = ('.jpg', '.png', '.gif', '.jpeg')

	def __init__(self, id, name, parent, disk, *args, **kwargs):

		self.thumb		= kwargs.get('thumb')
		self.dimensions	= kwargs.get('dimensions')
		self.exif		= kwargs.get('exif')

		self._exif_data = None

		CatalogFile.__init__(self, id, name, parent, disk, *args, **kwargs)


	@property
	def exif_data(self):
		if self._exif_data is None and self.exif is not None:
			try:
				self._exif_data = dict(eval(self.disk.catalog.data_provider.get_data(self.exif)))
			except:
				_LOG.exception('FileImage.exif_data file=%s' % self.name)
				self._exif_data = None
		return self._exif_data


	@property
	def image(self):
		if self.thumb is None:
			return None
		return self.disk.catalog.data_provider.get_data(self.thumb)


	def _get_info(self):
		result = CatalogFile._get_info(self)
		if self.dimensions is not None:
			result.append((50, _('Dimensions'), "%d x %d" % self.dimensions))
		exif = self.exif_data
		if exif is not None:
			for exif_key in ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'EXIF DateTime'):
				if exif.has_key(exif_key):
					try:
						ddate = time.strptime(exif[exif_key], '%Y:%m:%d %H:%M:%S')
						result.append((51, _('Date'), time.strftime('%c', ddate)))
						break
					except:
						_LOG.exception('_get_info key=%s' % exif_key)
						pass

			if exif.has_key('Image Model'):
				result.append((52, _('Camera'), "%s %s" % (exif.get('Image Make'), exif['Image Model'])))

			#if exif.has_key('EXIF UserComment'):
			#	result.append((52, _('User comment'), str(exif.get('EXIF UserComment'))))
		
			# informacje o zdjeciu
			shot_info = self.__get_exif_shotinfo(exif)
			if len(shot_info) > 0:
				result.append((53, _('Shot info'), ';   '.join(('%s:%s' % keyval for keyval in shot_info))))



		return result

	info = property(_get_info)


	def load(self, path, options, on_update):
		if CatalogFile.load(self, path, options, on_update):
			self._load_thumb(path)
			if os.path.splitext(path)[1].lower() in ('.jpg', '.jpeg'):
				self._load_exif(path)
			return True
		return False


	def update(self, path, options, on_update):
		changes, process = CatalogFile.update(self, path, options, on_update)
		if process:
			if changes or options.get('force', False):
				self._load_thumb(path)
				if os.path.splitext(path)[1].lower() in ('.jpg', '.jpeg'):
					self._load_exif(path)
			return True
		return False


	def _load_exif(self, path):
		_LOG.debug('FileImage._load_exif(%s)' % path)
		try:
			#jpeg_file = open(path, 'rb')
			#exif = EXIF.process_file(jpeg_file)
			image = PILImage.open(path)
			exif = image._getexif()
			if exif is not None:
				self._exif_data = {}
				for key, val in exif.iteritems():
					key = TAGS.get(key, key)
					if key in _IGNORE_EXIF_KEYS or key.startswith('Thumbnail '):
						continue
					if isinstance(val, str):
						val = val.printable.replace('\0', '').strip()
						val = ''.join(( zn for zn in val if zn in string.printable )) # wolne!!
					self._exif_data[key] = val
				if len(self._exif_data) > 0:
					str_exif = repr(self._exif_data)
					self.exif = self.disk.catalog.data_provider.append(str_exif)
				else:
					self.exif = None
		except StandardError:
			_LOG.exception('load_exif error file=%s' % path)
			self.exif = None
		#finally:
		#	if jpeg_file is not None:
		#		jpeg_file.close()


	def _load_thumb(self, path):
		_LOG.debug('FileImage._load_thumb(%s)' % path)
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

			thumbsize = os.path.getsize(tmpfilename)

			image = open(tmpfilename, 'rb')
			self.thumb = self.disk.catalog.data_provider.append(image.read(thumbsize))
			image.close()

		except StandardError:
			_LOG.exception('PILImage error file=%s' % path)
			self.thumb = None

		if os.path.exists(tmpfilename):
			os.unlink(tmpfilename)


	def __get_exif_shotinfo(self, exif):
		shot_info = []

		def append(key, name):
			if exif.has_key(key):
				shot_info.append((name, exif[key]))

		append('EXIF ExposureTime', _('t'))

		if exif.has_key('EXIF FNumber'):
			try:
				fnumber = eval(exif['EXIF FNumber'] + '.')
				if int(fnumber) == fnumber: 	fnumber = int(fnumber)
				shot_info.append((_('f'), fnumber))
			except:
				_LOG.exception('_get_info exif fnumber "%s"' % exif.get('EXIF FNumber'))

		if exif.has_key('EXIF ISOSpeedRatings'):
			shot_info.append((_('iso'), exif['EXIF ISOSpeedRatings']))
		elif exif.has_key('MakerNote ISOSetting'):
			try:
				iso = exif['MakerNote ISOSetting'][1:-1].split(',')[-1].strip()
				shot_info.append((_('iso'), iso))
			except:
				_LOG.exception('_get_info exif iso "%s"' % exif.get('MakerNote ISOSetting'))

		append('EXIF Flash', _('flash'))
		append('EXIF FocalLength', _('focal len'))

		return shot_info


	@classmethod
	def _attrlist(cls):
		attribs = CatalogFile._attrlist()
		attribs.extend((('thumb', tuple), ('dimensions', tuple), ('exif', tuple)))
		return attribs


# vim: encoding=utf8: ff=unix:
