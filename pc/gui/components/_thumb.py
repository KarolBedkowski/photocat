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

import cStringIO

import wx



class Thumb:
	def __init__(self, image):
		self._caption = image.name
		self.assigned_object = image
		
		try:
			stream = cStringIO.StringIO(image.image)
			img = wx.ImageFromStream(stream)
		except:
			_LOG.exception('Thumb.__init__/LoadImages  %r' % image)
			img = wx.EmptyImage(1, 1)		
		
		self._img = img
		self._bitmap = img.ConvertToBitmap()
		self._org_img_width = self.imgwidth = img.GetWidth()
		self._org_img_height = self.imgheight = img.GetHeight()


	def get_bitmap(self, width, height):
		if width < self.imgwidth or height < self.imgheight:
			scale = max(float(width) / self._org_img_width, float(height) / self._org_img_height)
			self.imgwidth = int(self._org_img_width * scale)
			self.imgheight = int(self._org_img_height * scale)
			img = self._img.Scale(self.imgwidth, self.imgheight)
			bmp = self._bitmap = img.ConvertToBitmap()
		else:
			bmp = self._bitmap
		
		return bmp
	
	
	def get_caption(self, width):
		end = len(self._caption)-1
		
		dc = wx.MemoryDC()
		bmp = wx.EmptyBitmap(10,10)
		dc.SelectObject(bmp)
		
		caption = None
		while end > 0:
			caption = self._caption[:end]
			sw, sh = dc.GetTextExtent(capion)
			if sw <= width:
				break
			
			end -= 1
			
		dc.SelectObject(wx.NullBitmap)

		return caption


# vim: encoding=utf8: ff=unix:
