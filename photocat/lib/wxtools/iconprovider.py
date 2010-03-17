#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#### p##ylint#: disable-msg=W0401, C0103
"""
Icon provider for windows

Copyright (c) Karol Będkowski, 2007

This file is part of kPyLibs
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'
__all__ = ['IconProvider']


import logging
import os.path

import wx

from photocat.lib.singleton import Singleton

_LOG = logging.getLogger(__name__)


class _IconProviderCache(Singleton):
	''' cache ikon '''

	def _init(self, icons, icons_directory):
		self.__icon_cache = {}
		self.__icons = icons
		self.__icons_dir = icons_directory

	def __load_icon(self, name):
		''' Zaladowanie podanej grafiki do cache '''

		bitmap = wx.ArtProvider_GetBitmap(name)
		if bitmap.IsNull():
			bitmap = None
			if self.__icons_dir:
				bitmap = self._try_to_load_from_dir(name)
			if bitmap is None and self.__icons is not None:
				attrname = 'get_%s_Image' % name
				if hasattr(self.__icons, attrname):
					bitmap = getattr(self.__icons, attrname)()
			if bitmap is None:
				_LOG.warn('_IconProviderCache.__load_icon(%s): not found' % name)
				bitmap = wx.NullBitmap
			else:
				self.__icon_cache[name] = bitmap
		return bitmap

	def __getitem__(self, name):
		icon = self.__icon_cache.get(name)
		if not icon:
			icon = self.__load_icon(name)
		return icon

	def __contains__(self, key):
		return key in self.__icon_cache

	def _try_to_load_from_dir(self, name):
		filename = os.path.join(self.__icons_dir, name + '.png')
		if not os.path.isfile(filename):
			return None
		bitmap = None
		try:
			bitmap = wx.Bitmap(filename, wx.BITMAP_TYPE_PNG)
		except IOError, err:
			_LOG.debug('_IconProviderCache._try_to_load_from_dir(%s): %s',
					name, str(err))
		else:
			if bitmap and bitmap.IsNull():
				bitmap = None
		return bitmap


class IconProvider:
	""" Klasa dostarczająca ikonki """

	def __init__(self, icons=None, data_dir=None):
		self.__image_list = wx.ImageList(16, 16)
		self.__image_dict = {}
		self._icon_provider_cache = _IconProviderCache(icons, data_dir)

	def get_image_list(self):
		""" ip.get_image_list() -> list -- pobranie listy ikon """
		return self.__image_list

	def load_icon(self, name):
		''' ip.load_icon(name) -> image -- zaladowanie podanej ikonki '''

		if name in self.__image_dict:
			return self.__image_list.GetBitmap(self.__image_dict[name])

		try:
			image = wx.ArtProvider_GetIcon(name)
			if image.IsNull():
				image = self._icon_provider_cache[name]
		except (KeyError, AttributeError):
			_LOG.exception('load_icon(%s) error' % name)
			image = wx.EmptyBitmap(1, 1)
		else:
			if isinstance(image, wx.Icon):
				self.__image_dict[name] = self.__image_list.AddIcon(image)
			elif isinstance(image, wx.Bitmap):
				self.__image_dict[name] = self.__image_list.Add(image)
			else:
				self.__image_dict[name] = self.__image_list.Add(image.ConvertToBitmap())
		return image

	def load_icons(self, names):
		''' ip.load_icons(names list) -> [images] -- zaladowanie listy ikon '''
		return [self.load_icon(name) for name in names]

	def get_image_index(self, name):
		''' ip.get_image_index(name) -> index -- pobranie indexu obrazka '''
		return self.__image_dict.get(name)

	def get_image(self, name):
		''' ip.get_image(name) -> image -- pobranie obrazka '''
		return self.load_icon(name)

	def get_icon(self, name):
		''' ip.get_icon(name) -> icon -- pobranie ikonku '''
		image = self.load_icon(name)
		if isinstance(image, wx.Icon):
			icon = image

		elif image is not None:
			if isinstance(image, wx.Image):
				image = image.ConvertToBitmap()
			icon = wx.EmptyIcon()
			icon.CopyFromBitmap(image)
		else:
			icon = None

		return icon



# vim: encoding=utf8:
