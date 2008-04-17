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
import re
import logging
_LOG = logging.getLogger(__name__)

import wx

import Image as PILImage
import PngImagePlugin, JpegImagePlugin, GifImagePlugin
PILImage._initialized = 3

from pc.lib					import EXIF

from _catalog_file			import CatalogFile

_ = wx.GetTranslation



_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote', 'EXIF UserComment']
RE_REPLACE_EXPRESSION = re.compile(r'[\0-\037]', re.MULTILINE)



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
			date = self.__get_exif_shot_date(exif)
			if date is not None:
				result.append((51, _('Date'), date))

			if exif.has_key('Image Model'):
				result.append((52, _('Camera'), "%s %s" % (exif.get('Image Make'), exif['Image Model'])))

			# informacje o zdjeciu
			shot_info = self.__get_exif_shotinfo(exif)
			if len(shot_info) > 0:
				result.append((53, _('Settings'), ';   '.join(('%s:%s' % keyval for keyval in shot_info))))

		return result

	info = property(_get_info)


	def load(self, path, options, on_update):
		if CatalogFile.load(self, path, options, on_update):
			self._load_thumb(path, options)
			if os.path.splitext(path)[1].lower() in ('.jpg', '.jpeg'):
				self._load_exif(path)
			return True
		return False


	def update(self, path, options, on_update):
		changes, process = CatalogFile.update(self, path, options, on_update)
		if process:
			if changes or options.get('force', False):
				self._load_thumb(path, options)
				if os.path.splitext(path)[1].lower() in ('.jpg', '.jpeg'):
					self._load_exif(path)
			return True
		return False


	def _load_exif(self, path):
		_LOG.debug('FileImage._load_exif(%s)' % path)
		self.exif = None
		try:
			jpeg_file = open(path, 'rb')
			exif = EXIF.process_file(jpeg_file)
			if exif is not None:
				self._exif_data = {}
				for key, val in exif.iteritems():
					if (key in _IGNORE_EXIF_KEYS or key.startswith('Thumbnail ') or
							key.startswith('EXIF Tag ') or key.startswith('MakerNote Tag ')):
						continue

					val = str(val).replace('\0', '').strip()
					self._exif_data[key] = RE_REPLACE_EXPRESSION.sub(' ', val)

				if len(self._exif_data) > 0:
					str_exif = repr(self._exif_data)
					self.exif = self.disk.catalog.data_provider.append(str_exif)
		except StandardError:
			_LOG.exception('load_exif error file=%s' % path)
		finally:
			if jpeg_file is not None:
				jpeg_file.close()


	def _load_thumb(self, path, options):
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

			thumbsize = (options.get('thumb_width', 200), options.get('thumb_height', 200))
			thumb_compression = options.get('thumb_compression', 50)

			image.thumbnail(thumbsize, PILImage.ANTIALIAS)
			image.save(tmpfilename, "JPEG", quality=thumb_compression)

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

		if exif.has_key('EXIF FocalLength'):
			try:
				flen = eval(exif['EXIF FocalLength'] + '.')
				if int(flen) == flen: 	flen = int(flen)
				shot_info.append((_('focal len.'), flen))
			except:
				_LOG.exception('_get_info exif flen "%s"' % exif.get('EXIF FocalLength'))

		return shot_info


	def __get_exif_shot_date(self, exif):
		for exif_key in ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'EXIF DateTime'):
			if exif.has_key(exif_key):
				try:
					ddate = time.strptime(exif[exif_key], '%Y:%m:%d %H:%M:%S')
					return time.strftime('%c', ddate)
				except:
					_LOG.exception('_get_info key=%s val="%s"' % (exif_key, exif[exif_key]))
		return None



	@classmethod
	def _attrlist(cls):
		attribs = CatalogFile._attrlist()
		attribs.extend((('thumb', tuple), ('dimensions', tuple), ('exif', tuple)))
		return attribs


# vim: encoding=utf8: ff=unix:
