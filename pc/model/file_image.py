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


import time
import types
import logging
_LOG = logging.getLogger(__name__)

import wx

from kabes.tools.formaters		import format_human_size

from pc.engine.image		import load_thumb_from_file, load_exif_from_file

from _catalog_file			import CatalogFile

_ = wx.GetTranslation




class FileImage(CatalogFile):
	FV3_CLASS_NAME = 1048576 + 3

	# lista rozszerzeń plików, które są ładowane (obsługiwane)
	IMAGE_FILES_EXTENSION = dict( (key, None) for key in (
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
	))

	# list rozszerzeń plików, które są raw-ami
	IMAGE_FILES_EXTENSION_RAW = dict( (key, None) for key in ('nef', 'arw', 'srf', 'sr2', 'crw', 'cr2', 'kdc', 'dcr', 'raf', 'mef', 'mos',
		'mrw', 'orf', 'pef', 'ptx', 'x3f', 'raw', 'r3d', '3fr', 'erf'))


	def __init__(self, oid, name, parent, disk, *args, **kwargs):

		self.thumb		= kwargs.get('thumb')
		self.dimensions	= kwargs.get('dimensions')
		self.exif		= kwargs.get('exif')
		self.shot_date	= kwargs.get('shot_date')

		self._exif_data = None

		# format pliku wer 1
		if self.thumb and type(self.thumb) == types.TupleType:
			self.thumb = self.thumb[0]

		if self.exif and type(self.exif) == types.TupleType:
			self.exif = self.exif[0]

		CatalogFile.__init__(self, oid, name, parent, disk, *args, **kwargs)

		# czy plik jest raw-em
		self.is_raw = self.name and (self.name.split('.')[-1].lower() in self.IMAGE_FILES_EXTENSION_RAW)


	@property
	def exif_data(self):
		if self._exif_data is None and self.exif is not None:
			try:
				self._exif_data = dict(eval(self.disk.catalog.data_provider.get_data(self.exif)))

			except:
				_LOG.exception('FileImage.exif_data file=%s', self.name)
				self._exif_data = None

		return self._exif_data


	@property
	def image(self):
		if self.thumb is None:
			return None

		return self.catalog.data_provider.get_data(self.thumb)


	def _get_info(self):
		result = CatalogFile._get_info(self)
		if self.dimensions is not None:
			result.append((50, _('Dimensions'), "%d x %d" % self.dimensions))

		date = None
		if self.shot_date > 0:
			try:
				date = time.strftime('%c', time.localtime(self.shot_date))

			except:
				_LOG.exception('_get_info convert to date error shot_date=%r', self.shot_date)

			else:
				result.append((51, _('Date'), date))

		exif = self.exif_data
		if exif is not None:
			if date is None and self.shot_date is None:
				date = self.__get_exif_shot_date(exif)
				if date:
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

		if self.shot_date > 0:
			return self.shot_date

		self.__set_shot_date_from_exif(self.exif_data)

		return self.shot_date or self.date


	@property
	def data_objects_count(self):
		return (self.thumb and 1 or 0) + (self.exif and 1 or 0)


	##########################################################################


	def load(self, path, options, on_update):
		if CatalogFile.load(self, path, options, on_update):
			self.thumb, self.dimensions = load_thumb_from_file(path, options, self.disk.catalog.data_provider)
			self.exif, self._exif_data = load_exif_from_file(path, self.disk.catalog.data_provider)
			self.shot_date = None
			self.__set_shot_date_from_exif(self._exif_data)

			return True

		return False


	def update(self, path, options, on_update):
		changes, process = CatalogFile.update(self, path, options, on_update)
		if process:
			if changes or options.get('force', False):
				self.thumb, self.dimensions = load_thumb_from_file(path, options, self.disk.catalog.data_provider)
				self.exif, self._exif_data = load_exif_from_file(path, self.disk.catalog.data_provider)
				self.shot_date = None
				self.__set_shot_date_from_exif(self._exif_data)

			return True

		return False


	def fill_shot_date(self):
		if self.shot_date is None and self.exif is not None:
			self.__set_shot_date_from_exif(self.exif_data)


	##########################################################################


	def __get_exif_shotinfo(self, exif):
		shot_info = []

		def append(key, name):
			if key in exif:
				shot_info.append((name, exif[key]))

		append('EXIF ExposureTime', _('t'))

		def get_value(key, name):
			if key in exif:
				try:
					val = eval(exif[key] + '.')
					shot_info.append((name, int(val) if int(val) == val else val))
				
				except:
					_LOG.exception('_get_info exif %s "%s"', key, exif.get(key))

		get_value('EXIF FNumber', _('f'))

		if 'EXIF ISOSpeedRatings' in exif:
			shot_info.append((_('iso'), exif['EXIF ISOSpeedRatings']))

		elif 'MakerNote ISOSetting' in exif:
			try:
				iso = exif['MakerNote ISOSetting'][1:-1].split(',')[-1].strip()
				shot_info.append((_('iso'), iso))

			except:
				_LOG.exception('_get_info exif iso "%s"', exif.get('MakerNote ISOSetting'))

		append('EXIF Flash', _('flash'))
		get_value('EXIF FocalLength', _('focal len.'))

		return shot_info


	def __get_exif_shot_date_value(self, exif):
		for exif_key in ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'EXIF DateTime'):
			if exif_key in exif:
				try:
					value = exif[exif_key]
					return time.strptime(value, '%Y:%m:%d %H:%M:%S') if value != '0000:00:00 00:00:00' else None

				except:
					_LOG.exception('_get_info key=%s val="%s"', exif_key, exif[exif_key])

		return 0


	def __get_exif_shot_date(self, exif):
		ddate = self.__get_exif_shot_date_value(exif)
		return None if not ddate else time.strftime('%c', ddate)


	def __set_shot_date_from_exif(self, exif):
		if exif is None:
			return

		shot_date = self.__get_exif_shot_date_value(exif)
		if shot_date == 0:
			self.shot_date = 0

		elif shot_date is not None:
			self.shot_date = time.mktime(shot_date)



	##########################################################################


	@classmethod
	def _attrlist(cls):
		attribs = CatalogFile._attrlist()
		attribs.extend((('shot_date', int), ('thumb', tuple), ('dimensions', tuple), ('exif', tuple)))
		return attribs


# vim: encoding=utf8: ff=unix:
