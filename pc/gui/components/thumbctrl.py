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
import wx.lib.newevent

from _thumb import Thumb


(ThumbSelectionChangeEvent,		EVT_THUMB_SELECTION_CHANGE)		= wx.lib.newevent.NewEvent()
(ThumbDblClickEvent,			EVT_THUMB_DBCLICK)				= wx.lib.newevent.NewEvent()



class ThumbCtrl(wx.ScrolledWindow):
	def __init__(self, parent, wxid=wx.ID_ANY, status_wnd=None):
		wx.ScrolledWindow.__init__(self, parent, wxid, style=wx.BORDER_SUNKEN|wx.HSCROLL|wx.VSCROLL)
		
		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX))
		
		self._cols = 0
		self._thumb_width = 200
		self._thumb_height = 200
		
		self._status_wnd = status_wnd
		
		self._caption_font	= wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
		self._pen			= wx.Pen(wx.BLUE, 1, wx.DOT)
		self._brush			= wx.Brush(self.GetBackgroundColour(), wx.SOLID)
		
		self.clear()
		
		self.Bind(wx.EVT_SIZE, self.__on_resize)
		self.Bind(wx.EVT_PAINT, self.__on_paint)
		self.Bind(wx.EVT_LEFT_DOWN, self.__on_mouse_down)
		self.Bind(wx.EVT_LEFT_DCLICK, self.__on_mouse_dbclick)
		self.Bind(wx.EVT_RIGHT_DOWN, self.__on_mouse_right_down)
		self.Bind(wx.EVT_IDLE, self.__on_idle)


	def clear(self):
		self._items = []
		self._selected = -1
		self._selected_list = []
		self._padding = 0
		self._last_preloaded = -1
		
		self._update()
		self.Refresh()


	def show_dir(self, dir):
		if isinstance(dir, list) or isinstance(dir, tuple):
			images = dir
		else:
			images = dir.files
		
		self._items = [ Thumb(image) for image in images ]
		self._selected_list = []
		self._selected = -1
		self._last_preloaded = -1
		
		self.Scroll(0, 0)
		
		self._update()
		self.Refresh()
	

	def set_thumb_size(self, thumb_width, thumb_height):
		self._thumb_width = thumb_width
		self._thumb_height = thumb_height
		[ item.reset() for item in self._items ]
		self._update()
		
		
	def is_selected(self, idx):
		return idx in self._selected_list
	

	@property
	def selected_items(self):
		return self._selected_list
		
	@property
	def selected_item(self):
		return self._items[self._selected].image if self._selected > -1 else None
	
	#######################################################################################	
	
		
	def _update(self):
		width = self.GetClientSize().GetWidth()
		cols = max((width - 30) / self._thumb_width, 1)
		
		# przesuniecie x aby ikonki byly na środku
		padding = (width - cols * self._thumb_width) / (cols + 1)

		# muszą być jakieś odstępy między miniaturkami
		if padding < 6 and cols > 1:
			cols -= 1
			padding = (width -  cols * self._thumb_width) / (cols + 1)
			
		self._padding = padding
		self._cols = cols
		self._rows = math.ceil(len(self._items) / float(cols))
		
		self.SetVirtualSize((
			self._cols * (self._thumb_width + padding),
			self._rows * (self._thumb_height + 30) + 10
		))
		
		self.SetSizeHints(self._thumb_width + padding, self._thumb_height + 30)
		self.SetScrollRate((self._thumb_width + padding) / 4, (self._thumb_height + 30)/4)


	def _get_item_idx_on_xy(self, x, y):		
		col = (x - self._padding) / (self._thumb_width + self._padding)
		
		# sprawdzenie czy klikeniecie w obszar
		if col > self._cols or col < 0:
			return None
		
		# sprawdzenie, czy nie klikniecie miedzy miniaturkami
		if x > (col + 1) * (self._thumb_width + self._padding) + 5:
			return None	

		row = (y - 5) / (self._thumb_height + 30)

		if row < 0:
			row = 0

		index = row * self._cols + col
		
		if index >= len(self._items):
			index = -1

		return index


	##################################################################################


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

		dc.SetPen(self._pen)
		dc.SetBrush(self._brush)
		dc.SetFont(self._caption_font)
		dc.SetTextForeground("#7D7D7D")

		# items
		row = -1
		tw = self._thumb_width 
		th = self._thumb_height
		twm = tw + self._padding
		thm = th + 30
		twc = self._thumb_width - 10
		padding = self._padding
		
		has_selected = len(self._selected_list) > 0 

		for ii, item  in enumerate(self._items):
			col = ii % self._cols

			if col == 0:
				row += 1

			# pozycja
			tx = col * twm + padding
			ty = row * thm + 5

			# czy rysowac
			if not paintRect.Intersects(wx.Rect(tx, ty, twm, thm)):
				continue
			
			# zaznaczenie
			if has_selected:
				if ii in self._selected_list:
					dc.DrawRectangle(tx-3, ty-3, tw+6, th+25)
			
			img = item.get_bitmap(tw, th)
		
			# centrowanie
			txi = tx + (tw - item.imgwidth) / 2
			tyi = ty + (th - item.imgheight) / 2
			
			# rysowanie
			dc.DrawBitmap(img, txi, tyi, True)
			
			# caption
			caption, caption_width = item.get_caption(twc, dc)
			txc = tx + (tw - caption_width) / 2
			dc.DrawText(caption, txc, ty + th)
			
		dc.EndDrawing()
		

	def __on_resize(self, event):
		self._update()
		self.Refresh()
		
		
	def __on_mouse_down(self, event):
		x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())

		lastselected = self._selected
		self._selected = self._get_item_idx_on_xy(x, y)
		
		if event.ControlDown():
			if self.is_selected(self._selected):
				self._selected_list.remove(self._selected)
			else:
				self._selected_list.append(self._selected)

		elif event.ShiftDown():
			if self._selected != -1:
				begindex = self._selected
				endindex = lastselected

				if lastselected < self._selected:
					begindex = lastselected
					endindex = self._selected

				self._selected_list = []

				for ii in xrange(begindex, endindex+1):
					self._selected_list.append(ii)

			self._selected = lastselected

		else:
			if self._selected == -1:
				update = len(self._selected_list) > 0
				self._selected_list = []

			else:
				self._selected_list = []
				self._selected_list.append(self._selected)

		self.Refresh()
		self.SetFocus()
		
		if lastselected != self._selected:
			wx.PostEvent(self, ThumbSelectionChangeEvent(idx=self._selected))


	def __on_mouse_right_down(self, evt):
		x, y = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())

		lastselected = self._selected
		selected = self._get_item_idx_on_xy(x, y)		
		if self._selected != selected:
			self.__on_mouse_down(evt)


	def __on_mouse_dbclick(self, event):
		x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
		self._selected = self._get_item_idx_on_xy(x, y)
		if self._selected > -1:
			wx.PostEvent(self, ThumbDblClickEvent(idx=self._selected))


	def __on_idle(self, evt):
		# ładowanie w tle miniaturek
		if self.IsShownOnScreen():
			len_items = len(self._items)
			if self._last_preloaded <  len_items -1 :
				self._last_preloaded += 1
				self._items[self._last_preloaded].get_bitmap(self._thumb_width, self._thumb_height)
				if self._status_wnd is not None:
					self._status_wnd.SetStatusText("%d%%" % (100*self._last_preloaded/len_items), 1)
				evt.RequestMore(True)
			elif self._status_wnd:
				self._status_wnd.SetStatusText("", 1)	
		evt.Skip()
		
		
	

# vim: encoding=utf8: ff=unix: