#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
pc.engine.thumb_drawer
 -- engine do obsługi rysowania miniaturek

 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

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

import sys
import time

import wx

from pc.lib	import fonttools



class ThumbDrawer(object):

	GROUP_BY_NONE	= 0
	GROUP_BY_DATE	= 1
	GROUP_BY_PATH	= 2

	def __init__(self, parent):

		self._parent		= parent
		self._cols			= 0
		self._width			= 0
		self.thumb_width	= 200
		self.thumb_height	= 200
		self.show_captions	= True
		self.group_by		= ThumbDrawer.GROUP_BY_NONE

		self._padding		= 0
		self._items_pos		= []
		self._group_bars 	= []
		self._items			= []

		self._caption_font	= wx.Font(8, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.NORMAL, False)
		self._pen			= wx.Pen(wx.BLUE, 1, wx.DOT)
		self._pen_header	= wx.Pen(wx.Colour(160, 160, 160), 1, wx.SOLID)
		self._brush			= wx.Brush(parent.GetBackgroundColour(), wx.SOLID)
		self._header_font = wx.Font(10, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False)
		self._caption_color = wx.Colour(127, 127, 127)
		self._caption_raw_color	= wx.Colour(70, 70, 255)
		self._header_color = wx.Colour(127, 127, 127)


	def set_captions_font(self, fontdata):
		''' thumbctrl.set_captions_font(fontdata) -- ustawienie czcionek i odświerzenie

			@param fontdata - słownik z informacją o fontach
		'''
		self._caption_font = fonttools.data2font(fontdata, 'thumb',
				wx.Font(8, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False))
		self._caption_color = fonttools.str2color(fontdata.get('thumb_font_color', '127;127;127'))

		self._header_font = fonttools.data2font(fontdata, 'header',
				wx.Font(10, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False))
		self._header_color = fonttools.str2color(fontdata.get('header_font_color', '127;127;127'))
		self._pen_header	= wx.Pen(self._header_color, 1, wx.SOLID)

		color = fonttools.str2color(fontdata.get('thumb_raw_color'), wx.Colour(70, 70, 255))
		if fontdata.get('thumb_raw_custom_color', True):
			self._caption_raw_color = color

		else:
			self._caption_raw_color = self._caption_color


	def get_item_idx_on_xy(self, x, y):
		''' thumbctrl._get_item_idx_on_xy(x, y) -> int -- znalezienie indexu elementu o danej współrzędnych

			@param x	- pozycja x
			@param y	- pozycja y
			@return index elementu lub -1 jezeli brak
		'''
		for index, item, x1, y1, x2, y2, dummy in self._items_pos:
			if x >= x1 and x <= x2 and y >= y1 and y <= y2:
				return index

		return -1


	###################################################################################################################


	def draw(self, dc, paint_rect, selected=None):
		''' thumbctrl.draw(dc, paint_rect, selected) -- narysowanie miniaturek na wskazanym dc i we wskazanym obszarze.

			@param dc		- dc po którym będzie rysowanie
			@param paint_rect - wxRect gdzie będzie rysowane, jeżeli None - wszędzie
			@param selected	- lista zaznaczonych elementów (indeksów)
		'''
		dc.BeginDrawing()
		dc.SetPen(self._pen)
		dc.SetBrush(self._brush)
		dc.SetFont(self._caption_font)
		dc.SetTextForeground(self._caption_color)

		caption_color		= self._caption_color
		caption_raw_color	= self._caption_raw_color

		tw		= self.thumb_width
		th		= self.thumb_height
		twc		= self.thumb_width - 10

		if paint_rect is None:
			painty1 = -1
			painty2 = sys.maxint

		else:
			painty1 = paint_rect.y
			painty2 = paint_rect.height + painty1

		show_captions	= self.show_captions
		selected_bottom	= ((self._caption_height + 15) if show_captions else 6)
		has_selected	= len(selected) > 0 if selected is not None else False

		paint_rect_Intersects = paint_rect.Intersects
		dc_DrawBitmap = dc.DrawBitmap
		dc_SetTextForeground = dc.SetTextForeground
		dc_DrawText = dc.DrawText

		for ii, item, tx, ty, txwm, tyhm, rect in self._items_pos:
			# czy rysowac
			if paint_rect is not None and not paint_rect_Intersects(rect):
				continue

			# zaznaczenie
			if has_selected and ii in selected:
				dc.DrawRectangle(tx-3, ty-3, tw+6, th+selected_bottom)

			img = item.get_bitmap(tw, th)

			# centrowanie
			txi = tx + (tw - item.imgwidth) / 2
			tyi = ty + (th - item.imgheight) / 2

			# rysowanie
			dc_DrawBitmap(img, txi, tyi, True)

			# caption
			if show_captions:
				dc_SetTextForeground(caption_raw_color if item.is_raw else caption_color)
				caption, caption_width = item.get_caption(twc, dc)
				txc = tx + (tw - caption_width) / 2
				dc_DrawText(caption, txc, ty + th + 2)

		# group_bars
		if self.group_by > ThumbDrawer.GROUP_BY_NONE:
			dc.SetFont(self._header_font)
			dc.SetPen(self._pen_header)
			dc.SetTextForeground(self._header_color)

			width = self._width - 20
			dc_DrawLine = dc.DrawLine

			for date, y1, y2 in self._group_bars:
				if painty1 <= y2 and y1 <= painty2:
					dc_DrawLine(10, y2, width, y2)
					dc_DrawText(str(date), 10, y1)

		dc.EndDrawing()


	def update(self, items, width, height=sys.maxint, dc=None):
		''' thumbctrl.update(items, width, [height]) -> tuple() -- aktualizacja rozmiarów i pozycji miniaturek

			@param items	- elementy do wyświetlenia
			@param width	- szerokość
			@param height	- wysokosc (max) default=inf.
			@return (cols, rows, virtual_size, size_hints, scroll_rate)
		'''

		self._items			= items
		self._items_pos		= []
		self._group_bars	= []

		cols = max((width - 30) / self.thumb_width, 1)

		# przesuniecie x aby ikonki byly na środku
		padding = (width - cols * self.thumb_width) / (cols + 1)

		# muszą być jakieś odstępy między miniaturkami
		if padding < 6 and cols > 1:
			cols -= 1
			padding = (width -  cols * self.thumb_width) / (cols + 1)

		self._padding	= padding
		self._cols		= cols

		# obliczenie wysokości etykiet
		self._caption_height, self._header_height = self._compute_captions_height(
				(self._caption_font, self._header_font),
				dc
		)

		# wyznaczenie pozycji miniaturek
		if len(self._items) == 0:
			rows, height, last_index = 0, 0, 0

		elif self.group_by == ThumbDrawer.GROUP_BY_DATE:
			rows, height, last_index = self.__compute_thumbs_pos_timeline(height)

		elif self.group_by == ThumbDrawer.GROUP_BY_PATH:
			rows, height, last_index = self.__compute_thumbs_pos_path(height)

		else:
			rows, height, last_index = self.__compute_thumbs_pos_normal(height)

		self._rows	= rows
		self._width = width

		return (cols, rows,
				(self._cols * (self.thumb_width + padding), height),
				(self.thumb_width + padding, self.thumb_height + 30),
				((self.thumb_width + padding) / 4, (self.thumb_height + 30) / 4),
				last_index
		)


	###################################################################################################################


	def __compute_thumbs_pos_normal(self, height):
		''' thumbctrl.__compute_thumbs_pos_normal() -- wyznaczenie pozycji poszczególnych miniaturek - normalne

			Pozycje miniaturek zapisywane są w self._item_pos jako
			(index, item, x1, y1, x2, y2, wxRect())

			@param height	- max wysokość
			@return (row, height, last_index) - liczba wierszy i długość panelu
		'''
		row		= -1
		tw		= self.thumb_width
		th		= self.thumb_height
		twm		= tw + self._padding
		thm		= th + ((self._caption_height + 20) if self.show_captions else 10)
		padding = self._padding
		cols	= self._cols

		max_rows = max(int((height - 10) / thm), 1) - 1

		items_pos = self._items_pos
		items_pos_append = items_pos.append

		for ii, item  in enumerate(self._items):
			col = ii % cols

			if col == 0:
				if row == max_rows:
					break

				row += 1

			# pozycja
			tx = col * twm + padding
			ty = row * thm + 5

			items_pos_append((ii, item, tx, ty, tx+tw, ty+thm, wx.Rect(tx, ty, twm, thm)))

		return row, ty+thm, len(items_pos)


	def __compute_thumbs_pos_timeline(self, height):
		''' thumbctrl.__compute_thumbs_pos_timeline() -- wyznaczenie pozycji poszczególnych miniaturek dla grupowania wg dnia

			Pozycje miniaturek zapisywane są w self._item_pos jako
			(index, item, x1, y1, x2, y2, wxRect())

			@param height	- max wysokość
			@return (row, height, last_index) - liczba wierszy i długość panelu
		'''

		def item_value_func(item):
			return time.localtime(item.image.date_to_check)[:3]

		def group_label_func(item):
			return time.strftime('%x', time.localtime(item.image.date_to_check))

		return self.__compute_thumbs_pos_group_by(height, item_value_func, group_label_func)


	def __compute_thumbs_pos_path(self, height, level=86400):
		''' thumbctrl.__compute_thumbs_pos_path() -- wyznaczenie pozycji poszczególnych miniaturek dla grupowania wg dnia

			Pozycje miniaturek zapisywane są w self._item_pos jako
			(index, item, x1, y1, x2, y2, wxRect())

			@param height	- max wysokość
			@param level	- [opcja] dzielnik daty do grupowania (w sek, 86400=dzień)
			@return (row, height, last_index) - liczba wierszy i długość panelu
		'''

		def item_value_func(item):
			return item.image.parent.path

		def group_label_func(item):
			return item.image.disk.name + ": " + item.image.parent.path

		return self.__compute_thumbs_pos_group_by(height, item_value_func, group_label_func)


	def __compute_thumbs_pos_group_by(self, height, item_value_func, group_label_func):
		''' thumbctrl.__compute_thumbs_pos_group_by() -- wyznaczenie pozycji poszczególnych miniaturek dla grupowania wg dnia

			Pozycje miniaturek zapisywane są w self._item_pos jako
			(index, item, x1, y1, x2, y2, wxRect())

			@param height	- max wysokość
			@param level	- [opcja] dzielnik daty do grupowania (w sek, 86400=dzień)
			@return (row, height, last_index) - liczba wierszy i długość panelu
		'''
		row			= -1
		col			= -1
		last_date	= -1

		tw		= self.thumb_width
		th		= self.thumb_height
		twm		= tw + self._padding
		thm		= th + ((self._caption_height + 20) if self.show_captions else 10)
		padding	= self._padding
		cols	= self._cols
		header_height = self._header_height

		items_pos		= self._items_pos
		items_pos_append = items_pos.append
		group_bars		= self._group_bars	= []
		group_bars_append = group_bars.append

		for index, item  in enumerate(self._items):
			col += 1
			item_date = item_value_func(item)

			if last_date != item_date:
				pos		= int((row + 1) * thm + 20)
				label	= group_label_func(item)
				col		= 0

				next_row = row + 1 + (header_height + 25)/float(thm)

				if (next_row + 1) * thm + 5 > height:
					break

				row			= next_row
				last_date	= item_date
				group_bars_append((label, pos, pos+header_height+2))

			elif col >= cols:
				col = 0

				if (row + 2) * thm + 5 > height:
					break

				row += 1

			# pozycja
			tx = col * twm + padding
			ty = int(row * thm + 5)

			items_pos_append((index, item, tx, ty, tx+tw, ty+thm, wx.Rect(tx, ty, twm, thm)))

		return row, ty+thm, len(items_pos)


	def _compute_captions_height(self, fonts, dest_dc):
		''' thumbctrl._compute_captions_height(fonts) -> [int] -- obliczenie wysokości napisów dla podanych fontów

			@param fonts -- [wxFont] | (wxFont) - lista fontów do przeliczenia
			@return lista wysokości w px podanych fontów
		'''
		dc = wx.ClientDC(self._parent) if dest_dc is None else dest_dc
		dc_SetFont = dc.SetFont
		dc_GetCharHeight = dc.GetCharHeight

		def compute(font):
			dc_SetFont(font)
			return dc_GetCharHeight()

		return ( compute(font) for font in fonts )




# vim: encoding=utf8: ff=unix:
