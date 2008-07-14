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
from pc.engine.thumb_drawer import ThumbDrawer

from _thumb import Thumb


(ThumbSelectionChangeEvent,		EVT_THUMB_SELECTION_CHANGE)		= wx.lib.newevent.NewEvent()
(ThumbDblClickEvent,			EVT_THUMB_DBCLICK)				= wx.lib.newevent.NewEvent()



class ThumbCtrl(wx.ScrolledWindow):
	''' Kontrolka wyświetlająca miniaturki obrazków '''

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

		self._thumb_drawer = ThumbDrawer(self)
		self.thumbs_preload = thumbs_preload
		self._status_wnd	= status_wnd

		self._items				= []
		self._selected_list		= []
		self._selected			= -1
		self._last_preloaded	= -1

		self.Bind(wx.EVT_SIZE,			self.__on_resize)
		self.Bind(wx.EVT_PAINT,			self.__on_paint)
		self.Bind(wx.EVT_LEFT_DOWN,		self.__on_mouse_down)
		self.Bind(wx.EVT_LEFT_DCLICK,	self.__on_mouse_dbclick)
		self.Bind(wx.EVT_RIGHT_DOWN,	self.__on_mouse_right_down)
		self.Bind(wx.EVT_IDLE,			self.__on_idle)


	def show_dir(self, images, sort_function=None):
		''' thumbctrl.show_dir(images) -- wyświetlenie listy miniaturek

			@param images - lista obiektów do wyświetlenia
			@param sort_function - funkcja sortująca [opcja]
		'''
		self._items			= [ Thumb(image) for image in images ]
		if sort_function is not None:
			self._items.sort(lambda x, y: sort_function(x.image, y.image))

		self._last_preloaded	= -1 if self.thumbs_preload else len(self._items)
		self._selected			= -1
		self._selected_list		= []

		self.Scroll(0, 0)
		self._update()


	def sort_current_dir(self, sort_function):
		''' thumbctrl.sort_current_dir(sort_function) -- posortowanie i odświeżenie widoku

			@param sort_function - funkcja sortująca
		'''
		self._items.sort(lambda x, y: sort_function(x.image, y.image))
		self._selected_list = []
		self._selected		= -1

		self.Scroll(0, 0)
		self._update()


	def set_thumb_size(self, thumb_width, thumb_height):
		''' thumbctrl.set_thumb_size(thumb_width, thumb_height) -- ustawienie nowego rozmiaru miniaturek i odświerzenie

			@param thumb_width		- nowa szerokość
			@param thumb_height		- nowa wysokość
		'''
		self._thumb_width	= thumb_width
		self._thumb_height	= thumb_height

		self._thumb_drawer.thumb_width	= thumb_width
		self._thumb_drawer.thumb_height = thumb_height

		[ item.reset() for item in self._items ]

		self._update()


	def update(self):
		self._update()


	@property
	def thumb_width(self):
		return self._thumb_width

	@property
	def thumb_height(self):
		return self._thumb_height


	def set_captions_font(self, fontdata):
		''' thumbctrl.set_captions_font(fontdata) -- ustawienie czcionek i odświerzenie

			@param fontdata - słownik z informacją o fontach
		'''
		self._thumb_drawer.set_captions_font(fontdata)
		self._update()


	@property
	def selected_items(self):
		''' thumbctrl.selected_items -> [] -- zwraca listę zaznaczonych obiektów '''
		return self._selected_list


	@property
	def selected_item(self):
		''' thumbctrl.selected_item -> item -- zwraca ostatni zaznaczony element lub None '''
		return self._items[self._selected].image if self._selected > -1 else None


	def _set_show_captions(self, show_captions):
		self._thumb_drawer.show_captions = show_captions

	def _get_show_captions(self):
		return self._thumb_drawer.show_captions

	show_captions = property(_get_show_captions, _set_show_captions)


	def _set_group_by(self, group_by):
		self._thumb_drawer.group_by = group_by

	def _get_group_by(self):
		return self._thumb_drawer.group_by

	group_by = property(_get_group_by, _set_group_by)

	#######################################################################################


	def _update(self):
		''' thumbctrl._update() -- aktualizacja rozmiarów i pozycji miniaturek '''

		width	= self.GetClientSize().GetWidth()
		res		= self._thumb_drawer.update(self._items, width)

		cols, rows, virtual_size, size_hints, scroll_rate, last_index = res

		self.SetVirtualSize(virtual_size)
		self.SetSizeHints(size_hints[0], size_hints[1])
		self.SetScrollRate(scroll_rate[0], scroll_rate[1])

		self.Refresh()


	##################################################################################


	def __on_paint(self, event):
		''' thumbctrl.__on_paint(event) -- callback na EVT_PAINT - przerysowanie kontrolki'''

		size = self.GetClientSize()
		paintRect = wx.Rect(0, 0, size.GetWidth(), size.GetHeight())
		paintRect.x, paintRect.y = self.GetViewStart()
		xu, yu = self.GetScrollPixelsPerUnit()
		paintRect.x = paintRect.x * xu
		paintRect.y = paintRect.y * yu

		dc = wx.PaintDC(self)
		self.PrepareDC(dc)
		self._thumb_drawer.draw(dc, paintRect, self._selected_list)


	def __on_resize(self, event):
		''' thumbctrl.__on_resize(event) -- callback na EVT_SIZE '''
		self._update()


	def __on_mouse_down(self, event):
		''' thumbctrl.__on_mouse_down(event) -- callback na EVT_LEFT_DOWN.
			Zaznacza/odznacza miniaturki.
		'''
		x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())

		lastselected = self._selected
		self._selected = self._thumb_drawer.get_item_idx_on_xy(x, y)

		if event.ControlDown():
			if self._selected in self._selected_list:
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
		''' thumbctrl.__on_mouse_right_down(evt) -- callback na EVT_RIGHT_DOWN '''

		x, y = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())

		lastselected = self._selected
		selected = self._thumb_drawer.get_item_idx_on_xy(x, y)
		if self._selected != selected:
			self.__on_mouse_down(evt)


	def __on_mouse_dbclick(self, event):
		''' thumbctrl.__on_mouse_dbclick(evt) -- callback na EVT_LEFT_DCLICK '''
		x, y = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
		self._selected = self._thumb_drawer.get_item_idx_on_xy(x, y)
		if self._selected > -1:
			wx.PostEvent(self, ThumbDblClickEvent(idx=self._selected))


	def __on_idle(self, evt):
		''' thumbctrl.__on_idle(evt) -- callback na EVT_IDLE - ładowanie w tle miniaturek '''
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
