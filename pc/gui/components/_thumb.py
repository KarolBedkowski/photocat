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



import logging
_LOG = logging.getLogger(__name__)

import wx

from pc.engine.image		import load_bitmap_from_item_with_size



class Thumb:
	''' Klasa obiektu miniaturki wyświtlanej w thumbctrl '''
	
	def __init__(self, image):
		self._caption = image.name[:-4] if len(image.name) > 4 else image.name
		self.image = image
		self.is_raw = image.is_raw
		self.reset()


	def reset(self):
		''' thumb.reset() -- reset wartości '''
		self._bitmap = None
		self.imgwidth = None
		self.imgheight = None
		self._last_caption_width = -1
		self._caption_width = -1


	#########################################################################


	def get_bitmap(self, width, height):
		''' thumb.get_bitmap(width, height) -> wxBitmap -- pobranie bitmapy obrazka

			@param width	- max szerokość
			@param height	- max wysokość
			@return wxBitmap - zmienjszony ewentualnie obrazek

			Bitmapa jest cachowana po 1 użyciu (o ile żądany rozmiar się nie zmienił)
		'''

		self._bitmap, self.imgwidth, self.imgheight = load_bitmap_from_item_with_size(self.image, width, height)
		return self._bitmap


	def get_caption(self, width, dc):
		''' thumb.get_caption(width, dc) -> (caption, caption_width) -- wyznaczenie rozmiaru podpisu

			@param width		- maksymalna szerokość napisu
			@param dc			- context
			@return (podpis, szerokość podpisu)
		'''
		if width == self._last_caption_width:
			return self._caption_prepared, self._caption_width

		end = len(self._caption)

		# ucinanie za długiego napisu
		caption = '.'
		while end > 0:
			caption = self._caption[:end]
			sw, sh = dc.GetTextExtent(caption)
			if sw <= width:
				self._caption_width = sw
				break

			end -= 1

		# doklejanie ... na koncu odcietego napisu
		if len(caption) < len(self._caption):
			if len(caption) > 4:
				caption = caption[:-4] + '...'

		self._caption_prepared = caption
		self._last_caption_width = width

		return caption, self._caption_width


# vim: encoding=utf8: ff=unix:
