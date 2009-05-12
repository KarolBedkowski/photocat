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


from collections import deque
import logging
_LOG = logging.getLogger(__name__)

import cStringIO
import re

import wx

import Image as PILImage
import PngImagePlugin, JpegImagePlugin, GifImagePlugin, TiffImagePlugin
import PpmImagePlugin, PcxImagePlugin, PsdImagePlugin, BmpImagePlugin, IcoImagePlugin, TgaImagePlugin
#PILImage._initialized = 3

from pc.lib					import EXIF



_CACHE = {}
_CACHE_LIST = deque()

_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote', 'EXIF UserComment']
_RE_REPLACE_EXPRESSION = re.compile(r'[\0-\037]', re.MULTILINE)


def clear_cache():
	_LOG.info('clear_cache count=%d', len(_CACHE))
	_CACHE.clear()
	_CACHE_LIST.clear()


def load_image_from_item(item):
	''' load_image_from_item(item) -> wx.Image -- załadowanie obrazka z katalogu.

		@return wxImage()
	'''

	img = None
	try:
		img		= wx.ImageFromStream(cStringIO.StringIO(item.image))

	except Exception, err:
		_LOG.exception('load_image_from_item %s error', item.name)

	return img or wx.EmptyImage(1, 1)


def load_bitmap_from_item(item):
	''' load_bitmap_from_item(item) -> wx.Bitmap -- załadowanie obrazka z katalogu.

		@return wxImage()
	'''
	img = load_image_from_item(item)
	return img.ConvertToBitmap() if img is not None else None


def load_bitmap_from_item_with_size(item, width, height):
	''' load_bitmap_from_item_with_size(item, width, height) -> wx.Bitmap -- załadowanie i ewentualne
			przeskalowanie obrazka

		@param item - element FileImage
		@param width - docelowa szerokość
		@param height - docelowa wysokość
		@return wxBitmap
	'''
	item_id = (id(item), width, height)
	if item_id in _CACHE:
		return _CACHE[item_id]

	img = load_image_from_item(item)
	img_width	= img.GetWidth()
	img_height	= img.GetHeight()

	scale = min(float(width) / img_width, float(height) / img_height, 1)
	if scale != 1:
		img_width	= int(img_width * scale)
		img_height	= int(img_height * scale)
		img = img.Scale(img_width, img_height)

	bitmap = img.ConvertToBitmap()

	result = bitmap, img_width, img_height

	if len(_CACHE_LIST) > 2000:
		del _CACHE[_CACHE_LIST.popleft()]

	_CACHE[item_id] = result

	return result



def load_thumb_from_file(path, options, data_provider):
	''' load_thumb_from_file(path, options, data_provider) -- ładowanie miniaturki z pliku i zapisanie katalogu

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

		if image.mode != 'RGB':
			image = image.convert('RGB')

		dimensions = image.size

		thumbsize = (options.get('thumb_width', 200), options.get('thumb_height', 200))
		thumb_compression = options.get('thumb_compression', 50)

		if dimensions[0] > thumbsize[0] or dimensions[1] > thumbsize[1]:
			image.thumbnail(thumbsize, PILImage.ANTIALIAS)

		# zapisanie miniaturki przez StringIO
		output = cStringIO.StringIO()
		image.save(output, "JPEG", quality=thumb_compression)
		thumb = data_provider.append(output.getvalue())
		output.close()

	except StandardError:
		_LOG.exception('load_thumb_from_file error file=%s', path)
		thumb = None

	return thumb, dimensions



def load_exif_from_file(path, data_provider):
	''' load_exif_from_file(path, data_provider) -- ładowanie exifa z pliku i zapisanie w katalogu

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
				if (key in _IGNORE_EXIF_KEYS or key.startswith('Thumbnail ') or
						key.startswith('EXIF Tag ') or key.startswith('MakerNote Tag ')):
					continue

				val = str(val).replace('\0', '').strip()
				exif_data[key] = _RE_REPLACE_EXPRESSION.sub(' ', val)

			if len(exif_data) > 0:
				str_exif = repr(exif_data)
				self_exif = data_provider.append(str_exif)

	except StandardError:
		_LOG.exception('load_exif_from_file error file=%s', path)

	finally:
		if jpeg_file is not None:
			jpeg_file.close()

	return self_exif, exif_data


# vim: encoding=utf8: ff=unix:
