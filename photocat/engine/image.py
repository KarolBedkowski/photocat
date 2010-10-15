#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
photocat.engine.image
-- engine do obsługi obrazów

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__revision__ = '$Id$'


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
#import PngImagePlugin, JpegImagePlugin, GifImagePlugin, TiffImagePlugin
#import PpmImagePlugin, PcxImagePlugin, PsdImagePlugin, BmpImagePlugin
#import IcoImagePlugin, TgaImagePlugin
#PILImage._initialized = 3

import pyexiv2

_PYEXIV2_1x = hasattr(pyexiv2, 'Image')


_LOG = logging.getLogger(__name__)
_IGNORE_EXIF_KEYS = ['JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote',
		'EXIF UserComment', 'Exif.Photo.MakerNote']
_RE_REPLACE_EXPRESSION = re.compile(r'[\0-\037]', re.MULTILINE)
_RE_RATIONAL = re.compile(r'^\d+/\d+$')
_EXIF_SHOTDATE_KEYS = ('EXIF DateTimeOriginal', 'EXIF DateTimeDigitized',
		'EXIF DateTime')


def load_bitmap_from_item_with_size(item, width, height, zoom):
	''' load_bitmap_from_item_with_size(item, width, height) -> wx.Bitmap
		-- załadowanie i ewentualne przeskalowanie obrazka

		@param item - element FileImage
		@param width - docelowa szerokość
		@param height - docelowa wysokość
		@return wxBitmap
	'''
	try:
		img = wx.ImageFromStream(cStringIO.StringIO(item.image))
		if not img.IsOk():
			img = wx.EmptyImage(1, 1)
			img_width = img_height = 1
	except IOError:
		_LOG.exception('load_bitmap_from_item_with_size %s error', item.name)
		img = wx.EmptyImage(1, 1)
		img_width = img_height = 1
	else:
		img_width = img.GetWidth()
		img_height = img.GetHeight()
		scale = min(float(width) / img_width, float(height) / img_height, zoom)
		if scale != 1:
			img_width = int(img_width * scale)
			img_height = int(img_height * scale)
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
		except OSError, err:
			_LOG.warn('load_thumb_from_file(%s) error: %s', (path, str(err)))
			image = PILImage.new('RGB', (1, 1))
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
#		jpeg_file = open(path, 'rb')
#		exif = EXIF.process_file(jpeg_file)
		if _PYEXIV2_1x:
			meta = pyexiv2.Image(path)
			meta.readMetadata()
			keys = meta.exifKeys()
			keys.extend(meta.iptcKeys())
		else:
			meta = pyexiv2.ImageMetadata(path)
			meta.read()
			keys = meta.exif_keys[:]
			#keys.extend(meta.xmp_keys)  # problems
			keys.extend(meta.iptc_keys)
		if keys:
			exif_data = {}
			for key in keys:
				val = meta[key]
				if (key in _IGNORE_EXIF_KEYS or key.startswith('Thumbnail ')
						or key.startswith('EXIF Tag ')
						or key.startswith('MakerNote Tag ')):
					continue
				if hasattr(val, 'raw_value'):
					val = val.raw_value
				elif hasattr(val, 'raw_values'):
					val = val.raw_values
				else:  # pyexiv2 1.x
					if hasattr(val, '__iter__'):
						val = ', '.join(str(val_) for val_ in val)
					val = str(val).replace('\0', '').strip()
					val = _RE_REPLACE_EXPRESSION.sub(' ', val)
				if len(val) > 97:
					val = val[:97] + '...'
				exif_data[key] = val
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
	''' Load Exif information from storage '''
	data = data_provider.get_data(exifidx)
	if data[0] == '\x80':
		try:
			return pickle.loads(data)
		except pickle.UnpicklingError:
			pass
	return dict(eval(data))


def get_exif_shot_date_value(exif):
	''' Get photo shot date from exif '''
	for exif_key in _EXIF_SHOTDATE_KEYS:
		if exif_key in exif:
			try:
				value = exif[exif_key]
				return (time.strptime(value, '%Y:%m:%d %H:%M:%S')
						if value != '0000:00:00 00:00:00' else None)
			except (ValueError, KeyError):
				_LOG.exception('_get_info key=%s val="%s"', exif_key,
						exif[exif_key])
	return 0


def get_exif_shotinfo(exif):
	''' Get information about photo from exif '''
	shot_info = []

	def __append(key, name):
		if key in exif:
			val = _convert_exif_val(key, exif[key])
			shot_info.append((name, val))

	__append('EXIF ExposureTime', _('t'))
	__append('Exif.Photo.ExposureTime', _('t'))

	def __get_value(key, name):
		if key in exif:
			try:
				val = eval(exif[key] + '.')
			except (KeyError, NameError):
				_LOG.exception('_get_info exif %s "%s"', key, exif.get(key))
			else:
				shot_info.append((name, int(val) if int(val) == val else val))

	__get_value('EXIF FNumber', _('f'))
	__append('Exif.Photo.FNumber', _('f'))

	if 'EXIF ISOSpeedRatings' in exif:
		__append('EXIF ISOSpeedRatings', _('iso'))
	elif 'MakerNote ISOSetting' in exif:
		try:
			iso = exif['MakerNote ISOSetting'][1:-1].split(',')[-1].strip()
		except KeyError:
			_LOG.exception('_get_info exif iso "%s"', exif.get('MakerNote ISOSetting'))
		else:
			shot_info.append((_('iso'), iso))
	elif 'Exif.Nikon3.ISOSettings' in exif:
		shot_info.append((_('iso'), exif['Exif.Nikon3.ISOSettings']))
	elif 'Exif.Nikon3.ISOSpeed' in exif:
		shot_info.append((_('iso'), exif['Exif.Nikon3.ISOSpeed']))
	elif 'Exif.ISOSpeedRatings' in exif:
		shot_info.append((_('iso'), exif['Exif.ISOSpeedRatings']))

	__append('EXIF Flash', _('flash'))
	__append('Exif.Photo.Flash', _('flash'))
	__get_value('EXIF FocalLength', _('focal len.'))
	__append('Exif.Photo.FocalLength', _('focal len.'))

	return shot_info


# list rozszerzeń plików, które są raw-ami
_IMAGE_FILES_EXTENSION_RAW = dict((key, None) for key in ('nef', 'arw', 'srf',
		'sr2', 'crw', 'cr2', 'kdc', 'dcr', 'raf', 'mef', 'mos',
		'mrw', 'orf', 'pef', 'ptx', 'x3f', 'raw', 'r3d', '3fr', 'erf'))


def is_file_raw(name):
	''' check is file is raw '''
	return (name and ('.' in name) \
			and os.path.splitext(name)[-1].lower()[1:] in _IMAGE_FILES_EXTENSION_RAW)


def _convert_exif_val(key, value):
	value = value.strip()
	if _RE_RATIONAL.match(value):
		try:
			num, den = value.split('/', 1)
			num = float(num)
			den = float(den)
		except:
			return value
		else:
			if num == 0:
				return '0'
			if den > num:
				return '1/%d' % (den / num)
			if int(num / den) == num / den:
				return str(int(num / den))
			return '%0.2f' % (num / den)
	return value


def get_tag_human(name, value):
	label = name
	hvalue = value
	if _PYEXIV2_1x:
		if ',' in value:
			value = ', '.join(_convert_exif_val(name, val)
					for val in value.split(','))
		else:
			value = _convert_exif_val(name, value)
		value = str(value).replace('\0', '').strip()
		hvalue = _RE_REPLACE_EXPRESSION.sub(' ', value)
		label = name.replace('.', ' ')
	else:
		if name.startswith('Exif.'):
			try:
				tag = pyexiv2.ExifTag(name)
				if tag:
					label = tag.label
					tag.raw_value = value
					if tag.human_value:
						hvalue = tag.human_value
			except KeyError:
				pass
		elif name.startswith('Iptc.'):
			try:
				tag = pyexiv2.IptcTag(name)
				if tag:
					label = 'IPTC ' + tag.title
					if isinstance(value, (list, tuple)):
						hvalue = ', '.join(value)
			except KeyError:
				pass
	hvalue = hvalue or value or ''
	if len(hvalue) > 97:
		hvalue = hvalue[:97] + '...'
	label = label or name
	if '\n' in label:
		label = label[:label.index('\n') - 1]
	return label or name, hvalue


def _rational2float(value):
	num, den = value.split('/', 1)
	num = float(num)
	den = float(den)
	return num / den


def exif_geopos_to_float(value):
	deg, mi, sec = map(_rational2float, value.split(None))
	return deg + mi / 60. + sec / 3600.


def get_geotag_from_exif(exif):
	#Exif.GPSInfo.GPSLatitude 51/1 6/1 66047/1927
	#Exif.GPSInfo.GPSLongitude 17/1 4/1 124887/2500
	if not 'Exif.GPSInfo.GPSLatitude' in exif or \
			not 'Exif.GPSInfo.GPSLongitude' in exif:
		return None
	lat = exif_geopos_to_float(exif['Exif.GPSInfo.GPSLatitude'])
	lon = exif_geopos_to_float(exif['Exif.GPSInfo.GPSLongitude'])
	return lat, lon




# vim: encoding=utf8: ff=unix
