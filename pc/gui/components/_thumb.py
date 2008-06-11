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

from pc.engine.image		import load_image_from_item



class Thumb:
	def __init__(self, image):
		self._caption = image.name[:-4] if len(image.name) > 4 else image.name
		self.image = image
		self.reset()


	def reset(self):
		self._bitmap = None
		self.imgwidth = None
		self.imgheight = None
		self._last_caption_width = -1
		self._caption_width = -1
	
	
	def _load_image(self):
		img = load_image_from_item(self.image)
		self.imgwidth = img.GetWidth()
		self.imgheight = img.GetHeight()
		return img


	def get_bitmap(self, width, height):
		img = None
		if self.imgwidth is None:
			img = self._load_image()

		if width < self.imgwidth or height < self.imgheight:
			if img is None:
				img = self._load_image()
				
			scale = min(float(width) / self.imgwidth, float(height) / self.imgheight)
			self.imgwidth = int(self.imgwidth * scale)
			self.imgheight = int(self.imgheight * scale)

			img = img.Scale(self.imgwidth, self.imgheight)

			self._bitmap = img.ConvertToBitmap()

		elif self._bitmap is None:
			self._bitmap = img.ConvertToBitmap()

		return self._bitmap
	
	
	def get_caption(self, width, dc):
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
