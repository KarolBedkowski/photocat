#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
pc.engine.image
 -- engine do obsługi obrazów

 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

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



import logging
import cStringIO
import re
import time
import os.path

try:
	import cPickle as pickle
except ImportError:
	import pickle

import wx
import Image as PILImage
import PngImagePlugin, JpegImagePlugin, GifImagePlugin, TiffImagePlugin
import PpmImagePlugin, PcxImagePlugin, PsdImagePlugin, BmpImagePlugin
import IcoImagePlugin, TgaImagePlugin
#PILImage._initialized = 3

from pc.lib import EXIF

_LOG = logging.getLogger(__name__)
_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote', 
		'EXIF UserComment']
_RE_REPLACE_EXPRESSION = re.compile(r'[\0-\037]', re.MULTILINE)

_EXIF_SHOTDATE_KEYS = ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 
		'EXIF DateTime')



def load_bitmap_from_item_with_size(item, width, height):
	''' load_bitmap_from_item_with_size(item, width, height) -> wx.Bitmap 
		-- załadowanie i ewentualne przeskalowanie obrazka

		@param item - element FileImage
		@param width - docelowa szerokość
		@param height - docelowa wysokość
		@return wxBitmap
	'''
	item_id = (id(item), width, height)
	try:
		img = wx.ImageFromStream(cStringIO.StringIO(item.image))

	except Exception, err:
		_LOG.exception('load_bitmap_from_item_with_size %s error', item.name)
		img = wx.EmptyImage(1, 1)
		img_width = img_height = 1

	else:
		img_width	= img.GetWidth()
		img_height	= img.GetHeight()
		scale = min(float(width) / img_width, float(height) / img_height, 1)
		if scale != 1:
			img_width	= int(img_width * scale)
			img_height	= int(img_height * scale)
			img = img.Scale(img_width, img_height)

	bitmap = img.ConvertToBitmap()
	result = (bitmap, img_width, img_height)
	return result


def load_thumb_from_file(path, options, data_provider):
	''' load_thumb_from_file(path, options, data_provider) -- ładowanie 
		miniaturki z pliku i zapisanie katalogu

		@param path		- ścieżka do pliku
		@param options	- opcje
		@param data_provider	- DataProvider
	'''
	_LOG.debug('load_thumb_from_file(%s)', path)
	dimensions = None
	thumb = None

	try:
		try:
			image = PILImage.open(path)
		except:
			image =  PILImage.new('RGB', (1, 1))
		else:
			if image.mode != 'RGB':
				image = image.convert('RGB')

			dimensions = image.size
			thumbsize = (options.get('thumb_width', 200), 
					options.get('thumb_height', 200))

			if dimensions[0] > thumbsize[0] or dimensions[1] > thumbsize[1]:
				image.thumbnail(thumbsize, PILImage.ANTIALIAS)

		# zapisanie miniaturki przez StringIO
		output = cStringIO.StringIO()
		thumb_compression = options.get('thumb_compression', 50)
		image.save(output, "JPEG", quality=thumb_compression)
		thumb = data_provider.append(output.getvalue())
		output.close()

	except StandardError:
		_LOG.exception('load_thumb_from_file error file=%s', path)
		thumb = None

	return thumb, dimensions



def load_exif_from_file(path, data_provider):
	''' load_exif_from_file(path, data_provider) -- ładowanie exifa z pliku 
		i zapisanie w katalogu

		@param path		- ścieżka do pliku
		@param data_provider	- DataProvider
	'''
	_LOG.debug('load_exif_from_file(%s)', path)
	self_exif = None
	exif_data = {}
	jpeg_file = None
	try:
		jpeg_file = open(path, 'rb')
		exif = EXIF.process_file(jpeg_file)
		if exif is not None:
			exif_data = {}
			for key, val in exif.iteritems():
				if (key in _IGNORE_EXIF_KEYS or key.startswith('Thumbnail ') 
						or key.startswith('EXIF Tag ') 
						or key.startswith('MakerNote Tag ')):
					continue

				val = str(val).replace('\0', '').strip()
				exif_data[key] = _RE_REPLACE_EXPRESSION.sub(' ', val)

			if len(exif_data) > 0:
				str_exif = pickle.dumps(exif_data, -1)
				self_exif = data_provider.append(str_exif)

	except StandardError:
		_LOG.exception('load_exif_from_file error file=%s', path)

	finally:
		if jpeg_file is not None:
			jpeg_file.close()

	return self_exif, exif_data



def load_exif_from_storage(exifidx, data_provider):
	data  = data_provider.get_data(exifidx)
	if data[0] == '\x80':
		try:
			return pickle.loads(data)
		except pickle.UnpicklingError:
			pass
	return dict(eval(data))



def get_exit_shot_date_value(exif):
	for exif_key in _EXIF_SHOTDATE_KEYS:
		if exif_key in exif:
			try:
				value = exif[exif_key]
				return (time.strptime(value, '%Y:%m:%d %H:%M:%S') 
						if value != '0000:00:00 00:00:00' else None)
			except:
				_LOG.exception('_get_info key=%s val="%s"', exif_key, 
						exif[exif_key])
	return 0



def get_exif_shotinfo(exif):
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
		append('EXIF ISOSpeedRatings', _('iso'))

	elif 'MakerNote ISOSetting' in exif:
		try:
			iso = exif['MakerNote ISOSetting'][1:-1].split(',')[-1].strip()
			shot_info.append((_('iso'), iso))

		except:
			_LOG.exception('_get_info exif iso "%s"', 
					exif.get('MakerNote ISOSetting'))

	append('EXIF Flash', _('flash'))
	get_value('EXIF FocalLength', _('focal len.'))

	return shot_info


# list rozszerzeń plików, które są raw-ami
_IMAGE_FILES_EXTENSION_RAW = dict( (key, None) for key in ('nef', 'arw', 'srf', 
		'sr2', 'crw', 'cr2', 'kdc', 'dcr', 'raf', 'mef', 'mos',
		'mrw', 'orf', 'pef', 'ptx', 'x3f', 'raw', 'r3d', '3fr', 'erf'))


def is_file_raw(name):
	return '.' in name and os.path.splitext(name)[-1].lower() in _IMAGE_FILES_EXTENSION_RAW



# vim: encoding=utf8: ff=unix:
