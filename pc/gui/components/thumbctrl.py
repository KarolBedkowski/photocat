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

import math

import wx

from _thumb import Thumb


class ThumbCtrl(wx.ScrolledWindow):
	def __init__(self, parent, wxid=wx.ID_ANY):
		wx.ScrolledWindow.__init__(self, parent, wxid)
		
		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX))
		
		self._cols = 0
		self._thumb_width = 200
		self._thumb_height = 200
		
		self._caption_font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False)
		
		self.clear()
		
		self.Bind(wx.EVT_SIZE, self.__on_resize)
		self.Bind(wx.EVT_PAINT, self.__on_paint)
		
		
	def clear(self):
		self._items = []
		self._selected = -1
		self._selectedarray = []
		
		self._update()
		self.Refresh()
		
		
	def bind_on_char(self, func):
		""" TODO: remove """
		self.Bind(wx.EVT_CHAR, func)


	def ShowDir(self, dir):
		""" TODO: rename """
		if isinstance(dir, list) or isinstance(dir, tuple):
			images = dir
		else:
			images = dir.files
		
		self._items = [ Thumb(image) for image in images ]
		self._selectedarray = []
		
		self.Scroll(0, 0)
		
		self._update()
		self.Refresh()
		
			
	def SetPopupMenu(self, *argv, **kwargs):
		""" TODO: implement """
		pass
	

	def SetThumbSize(self, thumb_width, thumb_height):
		""" TODO: rename """
		self._thumb_width = thumb_width
		self._thumb_height = thumb_height
		self._update()
		
		
	def _update(self):
		width = self.GetClientSize().GetWidth()
		self._cols = max((width - 5)/(self._thumb_width + 5), 1)
		self._rows = math.ceil(len(self._items)/float(self._cols))
		
		self.SetVirtualSize((
			self._cols * (self._thumb_width + 5) + 5,
			self._rows * (self._thumb_height + 20) + 5
		))
			
		self.SetSizeHints(self._thumb_width + 28, self._thumb_height + 30)
		self.SetScrollRate((self._thumb_width + 5)/4, (self._thumb_height + 5)/4)


	def __on_paint(self, event):
		""" Handles The wx.EVT_PAINT Event For ThumbnailCtrl. """
		
		size = self.GetClientSize()
		paintRect = wx.Rect(0, 0, size.GetWidth(), size.GetHeight())
		paintRect.x, paintRect.y = self.GetViewStart()
		xu, yu = self.GetScrollPixelsPerUnit()
		paintRect.x = paintRect.x * xu
		paintRect.y = paintRect.y * yu
		
		dc = wx.PaintDC(self)
		self.PrepareDC(dc)
		dc.BeginDrawing()

		dc.SetPen(wx.Pen(wx.BLACK, 0, wx.TRANSPARENT))
		dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
		dc.SetFont(self._caption_font)

		# items
		row = -1
		tw = self._thumb_width 
		th = self._thumb_height
		twm = tw + 5
		thm = th + 20
		twc = self._thumb_width -10

		for ii, item  in enumerate(self._items):
			col = ii % self._cols

			if col == 0:
				row += 1

			tx = 5 + col * twm
			ty = 5 + row * thm
			
			# visible?
			if not paintRect.Intersects(wx.Rect(tx, ty, twm, thm)):
				continue
			
			img = item.get_bitmap(tw, th)
		
			txi = tx + (tw - item.imgwidth) / 2
			tyi = ty + (th - item.imgheight) / 2

			dc.DrawBitmap(img, txi, tyi, True)
			
			# caption
			caption, caption_width = item.get_caption(twc, self._caption_font)
			txc = tx + (tw - caption_width) / 2

			dc.SetTextForeground("#7D7D7D")
			dc.DrawText(caption, txc, ty + th)
			
		dc.EndDrawing()
		

	def __on_resize(self, event):
		self._update()
		self.Refresh()
		
		


# vim: encoding=utf8: ff=unix:
