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
import logging
_LOG = logging.getLogger(__name__)

import wx

from kabes.tools.formaters	import format_human_size

from pc.engine	import image	as eimage

from pc.model._catalog_file		import CatalogFile

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

	__slots__ = ('thumb', 'dimensions', 'exif', 'shot_date', '_exif_data', 
			'is_raw', '__weakref__')


	def __init__(self, oid, name, parent, disk, *args, **kwargs):
		self.thumb		= kwargs.get('thumb')
		self.dimensions	= kwargs.get('dimensions')
		self.exif		= kwargs.get('exif')
		self.shot_date	= kwargs.get('shot_date')

		self._exif_data = None

		CatalogFile.__init__(self, oid, name, parent, disk, *args, **kwargs)

		# czy plik jest raw-em
		self.is_raw = eimage.is_file_raw(self.name)


	@property
	def exif_data(self):
		if self._exif_data is None and self.exif is not None:
			try:
				self._exif_data = eimage.load_exif_from_storage(self.exif,
						self.catalog.data_provider)

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
				_LOG.exception('_get_info convert to date error shot_date=%r',
						self.shot_date)

			else:
				result.append((51, _('Date'), date))

		exif = self.exif_data
		if exif:
			if date is None and self.shot_date is None:
				ddate = eimage.get_exit_shot_date_value(exif)
				if ddate:
					result.append((51, _('Date'), time.strftime('%c', ddate)))

			if 'Image Model' in exif:
				result.append((52, _('Camera'), "%s %s" % (exif.get('Image Make'),
					exif['Image Model'])))

			# informacje o zdjeciu
			shot_info = eimage.get_exif_shotinfo(exif)
			if len(shot_info) > 0:
				result.append((53, _('Settings'),
						';   '.join(('%s:%s' % keyval for keyval in shot_info))))

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
			self.thumb, self.dimensions = eimage.load_thumb_from_file(path,
					options, self.catalog.data_provider)
			self.exif, self._exif_data = eimage.load_exif_from_file(path,
					self.catalog.data_provider)
			self.shot_date = None
			self.__set_shot_date_from_exif(self._exif_data)

			return True

		return False


	def update(self, path, options, on_update):
		changes, process = CatalogFile.update(self, path, options, on_update)
		if process:
			if changes or options.get('force', False):
				self.thumb, self.dimensions = eimage.load_thumb_from_file(path,
						options, self.catalog.data_provider)
				self.exif, self._exif_data = eimage.load_exif_from_file(path,
						self.catalog.data_provider)
				self.shot_date = None
				self.__set_shot_date_from_exif(self._exif_data)

			return True

		return False


	def fill_shot_date(self):
		if self.shot_date is None and self.exif is not None:
			self.__set_shot_date_from_exif(self.exif_data)


	##########################################################################


	def __set_shot_date_from_exif(self, exif):
		if exif is None:
			return

		shot_date = eimage.get_exit_shot_date_value(exif)
		if shot_date == 0:
			self.shot_date = 0

		elif shot_date is not None:
			self.shot_date = time.mktime(shot_date)


	##########################################################################


	@classmethod
	def _attrlist(cls):
		attribs = CatalogFile._attrlist()
		attribs.extend((('shot_date', int), ('thumb', tuple),
			('dimensions', tuple), ('exif', tuple)))
		return attribs


# vim: encoding=utf8: ff=unix:
