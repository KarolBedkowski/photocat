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
import time

import wx
import wx.lib.newevent

from pc.lib	import fonttools

from _thumb import Thumb


(ThumbSelectionChangeEvent,		EVT_THUMB_SELECTION_CHANGE)		= wx.lib.newevent.NewEvent()
(ThumbDblClickEvent,			EVT_THUMB_DBCLICK)				= wx.lib.newevent.NewEvent()



class ThumbCtrl(wx.ScrolledWindow):
	def __init__(self, parent, wxid=wx.ID_ANY, status_wnd=None, thumbs_preload=True, show_captions=True):
		''' ThumbCtrl(parent, [wxid], [status_wnd], [thumbs_preload]) -> new object -- konstruktor
		
			@param parent		-- okno nadrzędne
			@param wxid			-- id tworzonego obiektu
			@param status_wnd	-- okno, w którego statusbarze będzie ustawiany procent załadowania
			@param thumbs_preload	-- bool: włącza ładowanie w tle miniaturek
			@param show_captions	-- bool: włącza wyświetlanie podpisów
		'''
		wx.ScrolledWindow.__init__(self, parent, wxid, style=wx.BORDER_SUNKEN|wx.HSCROLL|wx.VSCROLL)
		
		self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX))
		
		self._cols = 0
		self._thumb_width = 200
		self._thumb_height = 200		
		self.thumbs_preload = thumbs_preload
		self.show_captions = show_captions
		self.group_by_date = False
		
		self._status_wnd = status_wnd
		
		self._caption_font	= wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
		self._pen			= wx.Pen(wx.BLUE, 1, wx.DOT)
		self._pen_timeline	= wx.Pen(wx.Colour(160, 160, 160), 1, wx.SOLID)
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
		self._items_pos = []
		self._timeline_bars = []
		
		self._update()
		self.Refresh()


	def show_dir(self, images):
		''' thumbctrl.show_dir(images) -- wyświetlenie listy miniaturek
		
			@param images - lista obiektów do wyświetlenia
		'''
		self._items = [ Thumb(image) for image in images ]
		self._selected_list = []
		self._selected = -1
		self._last_preloaded = -1 if self.thumbs_preload else len(self._items)
		
		self.Scroll(0, 0)
		
		self._update()
		self.Refresh()
	

	def set_thumb_size(self, thumb_width, thumb_height):
		self._thumb_width = thumb_width
		self._thumb_height = thumb_height
		[ item.reset() for item in self._items ]
		self._update()
		
	
	def set_captions_font(self, fontdata):
		font = fonttools.data2font(fontdata, 'thumb', wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
		self._caption_font = font
		
		timeline_font = fonttools.data2font(fontdata, 'thumb', wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
		timeline_font.SetPointSize(timeline_font.GetPointSize()+2)
		timeline_font.SetWeight(wx.BOLD)
		self._timeline_font = timeline_font
		
		
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
		
		rows, height = self.__compute_thumbs_pos()
		
		self._rows = rows
		
		self.SetVirtualSize((self._cols * (self._thumb_width + padding), height))
		
		self.SetSizeHints(self._thumb_width + padding, self._thumb_height + 30)
		self.SetScrollRate((self._thumb_width + padding) / 4, (self._thumb_height + 30)/4)
		



	def _get_item_idx_on_xy(self, x, y):
		''' thumbctrl._get_item_idx_on_xy(x, y) -> int -- znalezienie indexu elementu o danej współrzędnych
		
			@param x	- pozycja x
			@param y	- pozycja y
			@return index elementu lub -1 jezeli brak
		'''
		for index, item, x1, y1, x2, y2, dummy in self._items_pos:
			if x >= x1 and x <= x2 and y >= y1 and y <= y2:
				return index

		return -1


	##################################################################################


	def __on_paint(self, event):
		""" Handles The wx.EVT_PAINT Event For ThumbCtrl. """
		
		size = self.GetClientSize()
		paintRect = wx.Rect(0, 0, size.GetWidth(), size.GetHeight())
		paintRect.x, paintRect.y = self.GetViewStart()
		xu, yu = self.GetScrollPixelsPerUnit()
		paintRect.x = paintRect.x * xu
		paintRect.y = paintRect.y * yu
		
		painty1 = paintRect.y
		painty2 = size.GetHeight() + painty1
		
		dc = wx.PaintDC(self)
		self.PrepareDC(dc)
		dc.BeginDrawing()

		dc.SetPen(self._pen)
		dc.SetBrush(self._brush)
		dc.SetFont(self._caption_font)
		dc.SetTextForeground("#7D7D7D")

		show_captions = self.show_captions

		# items
		tw = self._thumb_width 
		th = self._thumb_height
		selected_bottom = (25 if show_captions else 6)
		twc = self._thumb_width - 10
		
		has_selected = len(self._selected_list) > 0		

		for ii, item, tx, ty, txwm, tyhm, rect in self._items_pos:
			# czy rysowac
			if not paintRect.Intersects(rect):
				continue
			
			# zaznaczenie
			if has_selected and ii in self._selected_list:
				dc.DrawRectangle(tx-3, ty-3, tw+6, th+selected_bottom)
			
			img = item.get_bitmap(tw, th)
		
			# centrowanie
			txi = tx + (tw - item.imgwidth) / 2
			tyi = ty + (th - item.imgheight) / 2
			
			# rysowanie
			dc.DrawBitmap(img, txi, tyi, True)
			
			# caption
			if show_captions:
				caption, caption_width = item.get_caption(twc, dc)
				txc = tx + (tw - caption_width) / 2
				dc.DrawText(caption, txc, ty + th)
				
		# timeline_bars
		if self.group_by_date:
			dc.SetFont(self._timeline_font)
			dc.SetPen(self._pen_timeline)
			
			for date, y1, y2 in self._timeline_bars:
				if painty1 <= y1 and y1 <= painty2:
					dc.DrawLine(0, y2, size.GetWidth(), y2)
					dc.DrawText(str(date), 10, y1)
			
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


	def __compute_thumbs_pos(self):
		''' thumbctrl.__compute_thumbs_pos() -- wyznaczenie pozycji poszczególnych miniaturek
		
			Pozycje miniaturek zapisywane są w self._item_pos jako
			(index, item, x1, y1, x2, y2, wxRect())
			
			@return (row, height) - liczba wierszy i długość panelu
		'''
		
		if len(self._items) == 0:
			return 0, 0
		
		if self.group_by_date:
			return self.__compute_thumbs_pos_timeline()
		
		row = -1
		show_captions = self.show_captions
		tw = self._thumb_width 
		th = self._thumb_height
		twm = tw + self._padding
		thm = th + (30 if show_captions else 10)
		selected_bottom = (25 if show_captions else 6)
		twc = self._thumb_width - 10
		padding = self._padding
		
		items_pos = self._items_pos = []
		
		for ii, item  in enumerate(self._items):
			col = ii % self._cols

			if col == 0:
				row += 1

			# pozycja
			tx = col * twm + padding
			ty = row * thm + 5
			
			items_pos.append((ii, item, tx, ty, tx+tw, ty+thm, wx.Rect(tx, ty, twm, thm)))
			
		return row, ty+thm
			
			
	def __compute_thumbs_pos_timeline(self, level=86400):
		''' thumbctrl.__compute_thumbs_pos() -- wyznaczenie pozycji poszczególnych miniaturek dla grupowania wg dnia
		
			Pozycje miniaturek zapisywane są w self._item_pos jako
			(index, item, x1, y1, x2, y2, wxRect())
			
			@param level -- [opcja] dzielnik daty do grupowania
			@return (row, height) - liczba wierszy i długość panelu
		'''
		row = -1
		show_captions = self.show_captions
		tw = self._thumb_width 
		th = self._thumb_height
		twm = tw + self._padding
		thm = th + (30 if show_captions else 10)
		selected_bottom = (25 if show_captions else 6)
		twc = self._thumb_width - 10
		padding = self._padding
		
		items_pos = self._items_pos = []
		timeline_bars = self._timeline_bars = []
		
		last_date = -1
		col = -1
		
		for ii, item  in enumerate(self._items):
			col += 1

			if last_date != int(item.image.date_to_check / level):
				pos = int((row+1) * thm + 20)
				label = time.strftime('%x', time.localtime(item.image.date_to_check))
				timeline_bars.append((label, pos, pos+20))
				col = 0				
				row += 1.2
				last_date = int(item.image.date_to_check / level)

			if col >= self._cols:
				col = 0
				row += 1

			# pozycja
			tx = col * twm + padding
			ty = int(row * thm + 5)
			
			items_pos.append((ii, item, tx, ty, tx+tw, ty+thm, wx.Rect(tx, ty, twm, thm)))
		
		return row, ty+thm
		
	

# vim: encoding=utf8: ff=unix:
