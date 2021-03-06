#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
photocat.engine.thumb_drawer
-- engine do obsługi rysowania miniaturek

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006-2010'
__revision__ = '$Id$'


import weakref
import logging
import sys
import time

import wx

from photocat.lib import fonttools
from photocat.lib.wxtools import iconprovider
from photocat.lib.appconfig import AppConfig

_LOG = logging.getLogger(__name__)


class ThumbDrawer(object):		# pylint: disable-msg=R0902
	''' Draw thumb '''

	GROUP_BY_NONE = 0
	GROUP_BY_DATE = 1
	GROUP_BY_PATH = 2

	def __init__(self, parent):

		self._parent = weakref.proxy(parent)
		self._cols = 0
		self._width = 0
		self.thumb_width = 200
		self.thumb_height = 200
		self.scale = 0
		self.show_captions = True
		self.group_by = ThumbDrawer.GROUP_BY_NONE

		self._padding = 0
		self._items_pos = []
		self._group_bars = []
		self._items = []

		self._caption_font = wx.Font(8, wx.DEFAULT, wx.FONTSTYLE_NORMAL,
				wx.NORMAL, False)
		self._pen = wx.Pen(wx.BLUE, 1, wx.DOT)
		self._pen_header = wx.Pen(wx.Colour(160, 160, 160), 1, wx.SOLID)
		self._brush = wx.Brush(parent.GetBackgroundColour(), wx.SOLID)
		self._header_font = wx.Font(10, wx.DEFAULT, wx.FONTSTYLE_NORMAL,
				wx.FONTWEIGHT_BOLD, False)
		self._caption_color = wx.Colour(127, 127, 127)
		self._caption_raw_color = wx.Colour(70, 70, 255)
		self._header_color = wx.Colour(127, 127, 127)

		self._caption_height, self._header_height = 0, 0
		self._rows = 0

		self._appconfig = AppConfig()

		self._bmp_raw = iconprovider.get_image('raw')
		self._bmp_exif = iconprovider.get_image('exif')

	def __del__(self):
		self._items_pos = None
		self._items = None

	def set_captions_font(self, fontdata):
		''' thumbctrl.set_captions_font(fontdata) -- ustawienie czcionek
		i odświerzenie
		@param fontdata - słownik z informacją o fontach '''
		self._caption_font = fonttools.data2font(fontdata, 'thumb',
				wx.Font(8, wx.DEFAULT, wx.FONTSTYLE_NORMAL,
				wx.FONTWEIGHT_NORMAL, False))
		self._caption_color = fonttools.str2color(
				fontdata.get('thumb_font_color', '127;127;127'))
		self._header_font = fonttools.data2font(fontdata, 'header',
				wx.Font(10, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,
				False))
		self._header_color = fonttools.str2color(
				fontdata.get('header_font_color', '127;127;127'))
		self._pen_header = wx.Pen(self._header_color, 1, wx.SOLID)
		color = fonttools.str2color(fontdata.get('thumb_raw_color'),
				wx.Colour(70, 70, 255))
		if fontdata.get('thumb_raw_custom_color', True):
			self._caption_raw_color = color
		else:
			self._caption_raw_color = self._caption_color

	def get_item_idx_on_xy(self, pos_x, pos_y):
		''' thumbctrl._get_item_idx_on_xy(x, y) -> int -- znalezienie indexu
		elementu o danej współrzędnych
		@param x	- pozycja x
		@param y	- pozycja y
		@return index elementu lub -1 jezeli brak '''
		for index, _item, ix1, iy1, ix2, iy2, dummy in self._items_pos:
			if pos_x >= ix1 and pos_x <= ix2 and pos_y >= iy1 and pos_y <= iy2:
				return index

		return -1

	############################################################################

	def draw(self, dc, paint_rect, selected=None):		# pylint: disable-msg=R0914
		''' thumbctrl.draw(dc, paint_rect, selected) -- narysowanie miniaturek
		na wskazanym dc i we wskazanym obszarze.
		@param dc		- dc po którym będzie rysowanie
		@param paint_rect - wxRect gdzie będzie rysowane, jeżeli None - wszędzie
		@param selected	- lista zaznaczonych elementów (indeksów)'''
		dc.BeginDrawing()
		dc.SetPen(self._pen)
		dc.SetBrush(self._brush)
		dc.SetFont(self._caption_font)
		dc.SetTextForeground(self._caption_color)

		caption_color = self._caption_color
		caption_raw_color = self._caption_raw_color
		thumb_w = self.thumb_width
		thumb_h = self.thumb_height
		twc = self.thumb_width - 10

		if paint_rect is None:
			painty1 = -1
			painty2 = sys.maxint
		else:
			painty1 = paint_rect.y
			painty2 = paint_rect.height + painty1

		show_captions = self.show_captions
		show_emblems = self._appconfig.get('settings', 'view_show_emblems', True)
		selected_bottom = ((self._caption_height + 15) if show_captions else 6)
		has_selected = len(selected) > 0 if selected is not None else False

		paint_rect_intersects = paint_rect.Intersects if paint_rect else None
		dc_DrawBitmap = dc.DrawBitmap
		dc_SetTextForeground = dc.SetTextForeground
		dc_DrawText = dc.DrawText
		scale = self.scale

		def draw_emblem(bmp, posx, posy):
			ex1 = posx - bmp.GetWidth()
			ey1 = posy - bmp.GetHeight()
			dc_DrawBitmap(bmp, ex1, ey1, True)
			return ex1 - 2

		for idx, item, thumb_x, thumb_y, _txwm, _tyhm, rect in self._items_pos:
			# czy rysowac
			if paint_rect is not None and not paint_rect_intersects(rect):
				continue

			# zaznaczenie
			if has_selected and idx in selected:
				dc.DrawRectangle(thumb_x - 3, thumb_y - 3, thumb_w + 6,
						thumb_h + selected_bottom)

			img = item.get_bitmap(thumb_w, thumb_h, scale)

			# centrowanie
			txi = thumb_x + (thumb_w - item.imgwidth) / 2
			tyi = thumb_y + (thumb_h - item.imgheight) / 2

			# rysowanie
			dc_DrawBitmap(img, txi, tyi, True)

			# emblems
			if show_emblems:
				eposy = thumb_y + thumb_h
				eposx = thumb_x + thumb_w
				if item.image.exif:
					eposx = draw_emblem(self._bmp_exif, eposx, eposy)
				if item.image.is_raw:
					eposx = draw_emblem(self._bmp_raw, eposx, eposy)

			# caption
			if show_captions:
				dc_SetTextForeground(
						caption_raw_color if item.image.is_raw else caption_color)
				caption, caption_width = item.get_caption(twc, dc)
				txc = thumb_x + (thumb_w - caption_width) / 2
				dc_DrawText(caption, txc, thumb_y + thumb_h + 2)

		# group_bars
		if self.group_by > ThumbDrawer.GROUP_BY_NONE:
			dc.SetFont(self._header_font)
			dc.SetPen(self._pen_header)
			dc.SetTextForeground(self._header_color)

			width = self._width - 20
			dc_DrawLine = dc.DrawLine

			for date, bar_y1, bar_y2 in self._group_bars:
				if painty1 <= bar_y2 and bar_y1 <= painty2:
					dc_DrawLine(10, bar_y2, width, bar_y2)
					dc_DrawText(str(date), 10, bar_y1)

		dc.EndDrawing()

	def update(self, items, width, height=sys.maxint, dc=None):
		''' thumbctrl.update(items, width, [height]) -> tuple() -- aktualizacja
		rozmiarów i pozycji miniaturek

		@param items	- elementy do wyświetlenia
		@param width	- szerokość
		@param height	- wysokosc (max) default=inf.
		@return (cols, rows, virtual_size, size_hints, scroll_rate)'''

		self._items = items
		self._items_pos = []
		self._group_bars = []
		cols = max((width - 30) / self.thumb_width, 1)

		# przesuniecie x aby ikonki byly na środku
		padding = (width - cols * self.thumb_width) / (cols + 1)

		# muszą być jakieś odstępy między miniaturkami
		if padding < 6 and cols > 1:
			cols -= 1
			padding = (width - cols * self.thumb_width) / (cols + 1)

		self._padding = padding
		self._cols = cols

		# obliczenie wysokości etykiet
		self._caption_height, self._header_height = self._compute_captions_height(
				(self._caption_font, self._header_font), dc)

		# wyznaczenie pozycji miniaturek
		if len(self._items) == 0:
			rows, height, last_index = 0, 0, 0
		elif self.group_by == ThumbDrawer.GROUP_BY_DATE:
			rows, height, last_index = self.__compute_thumbs_pos_timeline(height)
		elif self.group_by == ThumbDrawer.GROUP_BY_PATH:
			rows, height, last_index = self.__compute_thumbs_pos_path(height)
		else:
			rows, height, last_index = self.__compute_thumbs_pos_normal(height)

		self._rows = rows
		self._width = width

		return (cols, rows, (self._cols * (self.thumb_width + padding), height),
				(self.thumb_width + padding, self.thumb_height + 30),
				((self.thumb_width + padding) / 4, (self.thumb_height + 30) / 4),
				last_index)

	############################################################################

	def __compute_thumbs_pos_normal(self, height):		# pylint: disable-msg=R0914
		''' thumbctrl.__compute_thumbs_pos_normal() -- wyznaczenie pozycji
		poszczególnych miniaturek - normalne

		Pozycje miniaturek zapisywane są w self._items_pos jako
		(index, item, x1, y1, x2, y2, wxRect())

		@param height	- max wysokość
		@return (row, height, last_index) - liczba wierszy i długość panelu'''
		row = -1
		thumb_w = self.thumb_width
		thumb_h = self.thumb_height
		twm = thumb_w + self._padding
		thm = thumb_h + ((self._caption_height + 20) if self.show_captions else 10)
		padding = self._padding
		cols = self._cols

		max_rows = max(int((height - 10) / thm), 1) - 1

		items_pos = self._items_pos
		items_pos_append = items_pos.append

		for idx, item  in enumerate(self._items):
			col = idx % cols
			if col == 0:
				if row == max_rows:
					break
				row += 1

			# pozycja
			thumb_x = col * twm + padding
			thumb_y = row * thm + 5
			items_pos_append((idx, item, thumb_x, thumb_y, thumb_x + thumb_w,
				thumb_y + thm, wx.Rect(thumb_x, thumb_y, twm, thm)))

		return row, thumb_y + thm, len(items_pos)

	_GROUP_TIMELINE_FUNC = (
			lambda item: time.localtime(item.image.date_to_check)[:3],
			lambda item: time.strftime('%x',
				time.localtime(item.image.date_to_check)))

	def __compute_thumbs_pos_timeline(self, height):
		''' thumbctrl.__compute_thumbs_pos_timeline() -- wyznaczenie pozycji
		poszczególnych miniaturek dla grupowania wg dnia

		Pozycje miniaturek zapisywane są w self._items_pos jako
		(index, item, x1, y1, x2, y2, wxRect())

		@param height	- max wysokość
		@return (row, height, last_index) - liczba wierszy i długość panelu'''

		item_value_func, group_label_func = self._GROUP_TIMELINE_FUNC
		return self.__compute_thumbs_pos_group_by(height, item_value_func,
				group_label_func)

	_GROUP_PATH_FUNC = (
			lambda item: item.image.parent.path,
			lambda item: item.image.disk.name + ": " + item.image.parent.path)

	def __compute_thumbs_pos_path(self, height, _level=86400):
		''' thumbctrl.__compute_thumbs_pos_path() -- wyznaczenie pozycji
		poszczególnych miniaturek dla grupowania wg dnia

		Pozycje miniaturek zapisywane są w self._items_pos jako
		(index, item, x1, y1, x2, y2, wxRect())

		@param height	- max wysokość
		@param level	- [opcja] dzielnik daty do grupowania (w sek, 86400=dzień)
		@return (row, height, last_index) - liczba wierszy i długość panelu'''

		item_value_func, group_label_func = self._GROUP_PATH_FUNC
		return self.__compute_thumbs_pos_group_by(height, item_value_func,
				group_label_func)

	def __compute_thumbs_pos_group_by(self, height,		# pylint: disable-msg=R0914
				item_value_func, group_label_func):
		''' thumbctrl.__compute_thumbs_pos_group_by() -- wyznaczenie pozycji
		poszczególnych miniaturek dla grupowania wg dnia

		Pozycje miniaturek zapisywane są w self._items_pos jako
		(index, item, x1, y1, x2, y2, wxRect())

		@param height	- max wysokość
		@param level	- [opcja] dzielnik daty do grupowania (w sek, 86400=dzień)
		@return (row, height, last_index) - liczba wierszy i długość panelu'''
		row = -1
		col = -1
		last_date = -1

		thumb_w = self.thumb_width
		thumb_h = self.thumb_height
		twm = thumb_w + self._padding
		thm = thumb_h + ((self._caption_height + 20) if self.show_captions else 10)
		padding = self._padding
		cols = self._cols
		header_height = self._header_height

		items_pos = self._items_pos
		items_pos_append = items_pos.append
		group_bars = self._group_bars = []
		group_bars_append = group_bars.append

		for index, item  in enumerate(self._items):
			col += 1
			item_date = item_value_func(item)

			if last_date != item_date:
				pos = int((row + 1) * thm + 20)
				label = group_label_func(item)
				col = 0
				next_row = row + 1 + (header_height + 25) / float(thm)
				if (next_row + 1) * thm + 5 > height:
					break
				row = next_row
				last_date = item_date
				group_bars_append((label, pos, pos + header_height + 2))
			elif col >= cols:
				col = 0
				if (row + 2) * thm + 5 > height:
					break
				row += 1

			# pozycja
			thumb_x = col * twm + padding
			thumb_y = int(row * thm + 5)
			items_pos_append((index, item, thumb_x, thumb_y, thumb_x + thumb_w,
					thumb_y + thm, wx.Rect(thumb_x, thumb_y, twm, thm)))

		return row, thumb_y + thm, len(items_pos)

	def _compute_captions_height(self, fonts, dest_dc):
		''' thumbctrl._compute_captions_height(fonts) -> [int] -- obliczenie
		wysokości napisów dla podanych fontów

		@param fonts -- [wxFont] | (wxFont) - lista fontów do przeliczenia
		@return lista wysokości w px podanych fontów'''
		dc = wx.ClientDC(self._parent) if dest_dc is None else dest_dc
		dc_SetFont = dc.SetFont
		dc_GetCharHeight = dc.GetCharHeight

		def __compute(font):
			dc_SetFont(font)
			return dc_GetCharHeight()

		return (__compute(font) for font in fonts)


# vim: encoding=utf8: ff=unix:
