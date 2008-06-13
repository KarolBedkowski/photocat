#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
#### p##ylint#: disable-msg=W0401, C0103
"""
Icon provider for windows

 Copyright (c) Karol Będkowski, 2007

 This file is part of kPyLibs

 kPyLibs is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 S7AG is distributed in the hope that it will be useful, but WITHOUT ANY
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

__all__ = ['IconProvider']


import logging
_LOG = logging.getLogger(__name__)

import types

import wx

from singleton import Singleton

class _IconProviderCache(Singleton):
	''' cache ikon '''

	def init(self, icons):
		self.__icon_cache = {}
		self.__icons = icons


	def __load_icon(self, name):
		''' ipc.__load_icon(name) -> bitmap -- Zaladowanie podanej grafiki do cache '''

		try:
			bitmap = wx.ArtProvider_GetBitmap(name)
			if bitmap.IsNull():
				bitmap = getattr(self.__icons, 'get_%s_Bitmap' % name)()
		except (AttributeError, TypeError):
			_LOG.exception('_IconProviderCache.__load_icon(%s) error' % name)
			bitmap = wx.NullBitmap
		else:
			self.__icon_cache[name] = bitmap
		return bitmap


	def __getitem__(self, name):
		return self.__icon_cache.get(name, self.__load_icon(name))


	def get_keys(self):
		''' pobranie nazw ikon '''
		return self.__icon_cache.keys()


	def get_cache(self):
		''' pobranie listy okon '''
		return self.__icon_cache



class IconProvider:
	""" Klasa dostarczająca ikonki """

	def __init__(self, icons=None):
		self.__image_list = wx.ImageList(16, 16)
		self.__image_dict = {}

		self._icon_provider_cache = _IconProviderCache(icons)


	def get_image_list(self):
		""" ip.get_image_list() -> list -- pobranie listy ikon """
		return self.__image_list


	def load_icon(self, name):
		''' ip.load_icon(name) -> image -- zaladowanie podanej ikonki '''
		icon = False
		try:
			image = wx.ArtProvider_GetIcon(name)
			if image.IsNull():
				image = self._icon_provider_cache[name]
			else:
				icon = True
		except (KeyError, AttributeError):
			_LOG.exception('load_icon(%s) error' % name)
			image = wx.EmptyBitmap(1, 1)
		else:
			if icon:
				self.__image_dict[name] = self.__image_list.AddIcon(image)
			else:
				self.__image_dict[name] = self.__image_list.AddWithColourMask(image, wx.WHITE)
		return image


	def load_icons(self, names):
		''' ip.load_icons(names list) -> [images] -- zaladowanie listy ikon '''
		return [ self.load_icon(name) for name in names ]


	def get_image_index(self, name):
		''' ip.get_image_index(name) -> index -- pobranie indexu obrazka '''
		return self.__image_dict.get(name)


	def get_image(self, name):
		''' ip.get_image(name) -> image -- pobranie obrazka '''
		return self.load_icon(name)


	def get_icon(self, name):
		''' ip.get_icon(name) -> icon -- pobranie ikonku '''
		image = self.load_icon(name)
		if image is not None:
			icon = wx.EmptyIcon()
			icon.CopyFromBitmap(image)
		else:
			icon = None
		return icon



# vim: encoding=utf8:
