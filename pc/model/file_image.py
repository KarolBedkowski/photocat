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


import string
import time
import re
import types
import logging
_LOG = logging.getLogger(__name__)
import cStringIO

import wx

import Image as PILImage
import PngImagePlugin, JpegImagePlugin, GifImagePlugin, TiffImagePlugin
import TiffImagePlugin, PpmImagePlugin, PcxImagePlugin, PsdImagePlugin, BmpImagePlugin, IcoImagePlugin, TgaImagePlugin
#PILImage._initialized = 3

from kpylibs.formaters		import format_human_size

from pc.lib					import EXIF

from _catalog_file			import CatalogFile

_ = wx.GetTranslation



_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote', 'EXIF UserComment']
_RE_REPLACE_EXPRESSION = re.compile(r'[\0-\037]', re.MULTILINE)



class FileImage(CatalogFile):

	# lista rozszerzeń plików, które są ładowane (obsługiwane)
	IMAGE_FILES_EXTENSION = (
		'.jpg', '.jpe', '.jpeg',
		'.png', '.gif', '.bmp', '.ico', '.pcx', '.psd',
		'.ppm', '.pbm', '.pgm', '.pnm',
		'.tga', '.targa',
		'.tif', '.tiff',
		'.nef',						# nikon raw
		'.arw', '.srf', '.sr2',		# sony raw
		'.crw', '.cr2', 			# canon raw
		'.kdc', '.dcr',				# kodak raw
		'.raf',						# fuji raw
		'.mef', '.mos',				# mamiya raw
		'.mrw',						# minolta raw
		'.orf',						# olympus raw
		'.pef', '.ptx',				# pentax, samsung raw
		'.x3f',						# sigma raw
		'.raw',						# panasonic raw
		'.r3d',						# red raw
		'.3fr',						# hasselblad raw
		'.erf'						# epson raw
	)

	# list rozszerzeń plików, które są raw-ami
	IMAGE_FILES_EXTENSION_RAW = ('nef', 'arw', 'srf', 'sr2', 'crw', 'cr2', 'kdc', 'dcr', 'raf', 'mef', 'mos',
		'mrw', 'orf', 'pef', 'ptx', 'x3f', 'raw', 'r3d', '3fr', 'erf')


	def __init__(self, id, name, parent, disk, *args, **kwargs):

		self.thumb		= kwargs.get('thumb')
		self.dimensions	= kwargs.get('dimensions')
		self.exif		= kwargs.get('exif')
		self.shot_date	= kwargs.get('shot_date')

		self._exif_data = None

		# format pliku wer 1
		if self.thumb is not None and type(self.thumb) == types.TupleType:
			self.thumb = self.thumb[0]

		if self.exif is not None and type(self.exif) == types.TupleType:
			self.exif = self.exif[0]

		CatalogFile.__init__(self, id, name, parent, disk, *args, **kwargs)

		# czy plik jest raw-em
		self.is_raw = (self.name is not None) and (self.name.split('.')[-1].lower() in self.IMAGE_FILES_EXTENSION_RAW)


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

		date = None
		if self.shot_date:
			try:
				date = time.strftime('%c', time.localtime(self.shot_date))

			except:
				_LOG.exception('_get_info convert to date error shot_date=%r' % self.shot_date)

			else:
				result.append((51, _('Date'), date))

		exif = self.exif_data
		if exif is not None:
			if date is None:
				date = self.__get_exif_shot_date(exif)
				if date is not None:
					result.append((51, _('Date'), date))

			if 'Image Model' in exif:
				result.append((52, _('Camera'), "%s %s" % (exif.get('Image Make'), exif['Image Model'])))

			# informacje o zdjeciu
			shot_info = self.__get_exif_shotinfo(exif)
			if len(shot_info) > 0:
				result.append((53, _('Settings'), ';   '.join(('%s:%s' % keyval for keyval in shot_info))))

		if self.size is not None:
			result.append((201, _('File size'), format_human_size(self.size)))

		return result

	info = property(_get_info)


	@property
	def date_to_check(self):
		""" pobranie daty do wyszukania.
			Jeżeli nie jest wypełniony shot_date (wersja 2.1-) to próba pobrania z exifa.
			Jeżeli nie ma w exifie - data pliku.
		"""
		if self.shot_date is not None:
			return self.shot_date

		if self.exif is not None:
				shot_date = self.__get_exif_shot_date_value(self.exif_data)
				if shot_date is not None:
					self.shot_date = time.mktime(shot_date)

		return self.shot_date or self.date


	@property
	def data_objects_count(self):
		return (self.thumb and 1 or 0) + (self.exif and 1 or 0)


	##########################################################################


	def load(self, path, options, on_update):
		if CatalogFile.load(self, path, options, on_update):
			self._load_thumb(path, options)
			self._load_exif(path)
			self.shot_date = None
			if self._exif_data is not None:
				shot_date = self.__get_exif_shot_date_value(self._exif_data)
				if shot_date is not None:
					self.shot_date = time.mktime(shot_date)

			return True

		return False


	def update(self, path, options, on_update):
		changes, process = CatalogFile.update(self, path, options, on_update)
		if process:
			if changes or options.get('force', False):
				self._load_thumb(path, options)
				self._load_exif(path)
				self.shot_date = None
				if self._exif_data is not None:
					shot_date = self.__get_exif_shot_date_value(self._exif_data)
					if shot_date is not None:
						self.shot_date = time.mktime(shot_date)

			return True

		return False


	def fill_shot_date(self):
		if self.shot_date is None and self.exif is not None:
			exif = self.exif_data
			if exif is not None:
				shot_date = self.__get_exif_shot_date_value(exif)
				if shot_date is not None:
					self.shot_date = time.mktime(shot_date)


	##########################################################################


	def _load_exif(self, path):
		_LOG.debug('FileImage._load_exif(%s)' % path)
		self.exif = None
		jpeg_file = None
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
					self._exif_data[key] = _RE_REPLACE_EXPRESSION.sub(' ', val)

				if len(self._exif_data) > 0:
					str_exif = repr(self._exif_data)
					self.exif = self.disk.catalog.data_provider.append(str_exif)

		except StandardError:
			_LOG.exception('load_exif error file=%s' % path)

		finally:
			if jpeg_file is not None:
				jpeg_file.close()


	def _load_thumb(self, path, options):
		''' file_image._load_thumb(path, options) -- ładowanie miniaturki z pliku i zapisanie katalogu

			@param path		- ścieżka do pliku
			@param options	- opcje
		'''
		_LOG.debug('FileImage._load_thumb(%s)' % path)
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

			if self.dimensions[0] > thumbsize[0] or self.dimensions[1] > thumbsize[1]:
				image.thumbnail(thumbsize, PILImage.ANTIALIAS)

			# zapisanie miniaturki przez StringIO
			output = cStringIO.StringIO()
			image.save(output, "JPEG", quality=thumb_compression)
			self.thumb = self.disk.catalog.data_provider.append(output.getvalue())
			output.close()

		except StandardError:
			_LOG.exception('PILImage error file=%s' % path)
			self.thumb = None


	def __get_exif_shotinfo(self, exif):
		shot_info = []

		def append(key, name):
			if key in exif:
				shot_info.append((name, exif[key]))

		append('EXIF ExposureTime', _('t'))

		if 'EXIF FNumber' in exif:
			try:
				fnumber = eval(exif['EXIF FNumber'] + '.')
				if int(fnumber) == fnumber: 	fnumber = int(fnumber)
				shot_info.append((_('f'), fnumber))

			except:
				_LOG.exception('_get_info exif fnumber "%s"' % exif.get('EXIF FNumber'))

		if 'EXIF ISOSpeedRatings' in exif:
			shot_info.append((_('iso'), exif['EXIF ISOSpeedRatings']))

		elif 'MakerNote ISOSetting' in exif:
			try:
				iso = exif['MakerNote ISOSetting'][1:-1].split(',')[-1].strip()
				shot_info.append((_('iso'), iso))

			except:
				_LOG.exception('_get_info exif iso "%s"' % exif.get('MakerNote ISOSetting'))

		append('EXIF Flash', _('flash'))

		if 'EXIF FocalLength' in exif:
			try:
				flen = eval(exif['EXIF FocalLength'] + '.')
				if int(flen) == flen: 	flen = int(flen)
				shot_info.append((_('focal len.'), flen))

			except:
				_LOG.exception('_get_info exif flen "%s"' % exif.get('EXIF FocalLength'))

		return shot_info


	def __get_exif_shot_date_value(self, exif):
		for exif_key in ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'EXIF DateTime'):
			if exif_key in exif:
				try:
					value = exif[exif_key]
					return time.strptime(value, '%Y:%m:%d %H:%M:%S') if value != '0000:00:00 00:00:00' else None

				except:
					_LOG.exception('_get_info key=%s val="%s"' % (exif_key, exif[exif_key]))

		return None


	def __get_exif_shot_date(self, exif):
		ddate = self.__get_exif_shot_date_value(exif)
		return None if ddate is None else time.strftime('%c', ddate)


	##########################################################################


	@classmethod
	def _attrlist(cls):
		attribs = CatalogFile._attrlist()
		attribs.extend((('shot_date', int), ('thumb', tuple), ('dimensions', tuple), ('exif', tuple)))
		return attribs


# vim: encoding=utf8: ff=unix:
