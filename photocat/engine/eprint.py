#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
photocat.engine.eprint
-- engine do obsługi drukowania

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004, 2005, 2006

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


import logging

import wx

from photocat.gui.components._thumb import Thumb
from photocat.engine.thumb_drawer import ThumbDrawer

_LOG = logging.getLogger(__name__)


class _Printout(wx.Printout):
	''' Printing '''

	def __init__(self, items, options):
		wx.Printout.__init__(self)
		self.items = items
		self.drawer = ThumbDrawer(self)
		self._num_pages = 0
		self._items_per_page = []
		self._options = options
		self._log_units_mm = 0

		self.drawer.set_captions_font(options['fontdata'])
		self.drawer.thumb_width = options['thumb_width']
		self.drawer.thumb_height = options['thumb_height']
		self.drawer.show_captions = options['show_captions']
		self.drawer.group_by = options['group_by']

	def _calc_scale(self, dc):
		''' Calculate scaling factor '''
		ppi_printer_x, _ppi_printer_y = self.GetPPIPrinter()
		ppi_screen_x, _ppi_screen_y = self.GetPPIScreen()
		log_scale = float(ppi_printer_x) / float(ppi_screen_x)

		page_w, _ph = self.GetPageSizePixels()
		device_w, _dh = dc.GetSize()
		scale = log_scale * float(device_w) / float(page_w) / 2

		dc.SetUserScale(scale, scale)
		self._log_units_mm = float(ppi_printer_x) / (log_scale * 25.4)

	def _calc_layout(self, dc):
		''' Calculate layout '''
		px1, px2, py1, py2 = 5, 5, 5, 5

		device_w, device_h = dc.GetSize()
		px1 = px1 * self._log_units_mm
		py1 = py1 * self._log_units_mm
		px2 = dc.DeviceToLogicalXRel(device_w) - px2 * self._log_units_mm
		py2 = dc.DeviceToLogicalYRel(device_h) - py2 * self._log_units_mm

		page_height = int(py2 - py1)
		page_width = int(px2 - px1)

		dc.SetDeviceOrigin(px1, py1)

		# rysowanie marginesów
		#dc.DrawRectangleRect(wx.RectPP((px1, py1), (page_width-px2,
		#		page_height-py2)))

		return page_width, page_height

	def HasPage(self, page):		# pylint: disable-msg=C0103,W0221
		''' Check is page exists '''
		return page <= self._num_pages

	def GetPageInfo(self):		# pylint: disable-msg=C0103,W0221
		''' GetPageInfo '''
		return (1, self._num_pages, 1, self._num_pages)

	def OnPrintPage(self, page):		# pylint: disable-msg=C0103
		''' Render page '''
		dc = self.GetDC()

		self._calc_scale(dc)
		width, height = self._calc_layout(dc)

		#res =
		self.drawer.update(self._items_per_page[page - 1], width, height, dc=dc)
		#cols, rows, virtual_size, size_hints, scroll_rate, last_index = res

		self.drawer.draw(dc, None)

		return True

	def OnPreparePrinting(self):		# pylint: disable-msg=C0103,W0221
		''' Prepare to printing '''
		dc = self.GetDC()
		self._calc_scale(dc)
		width, height = self._calc_layout(dc)

		begin = 0
		last_index = -1
		self._num_pages = 0
		self._items_per_page = []
		while True:
			res = self.drawer.update(self.items[begin:], width, height, dc=dc)
			last_index = res[5]
			if last_index == 0:
				break

			self._items_per_page.append(self.items[begin:begin + last_index])
			begin += last_index
			self._num_pages += 1

	def GetBackgroundColour(self):		# pylint: disable-msg=C0103,R0201
		''' GetBackgroundColour '''
		return wx.WHITE


def print_preview(parent, print_data, images, options):
	''' Open print preview '''
	data = wx.PrintDialogData(print_data)
	images = [Thumb(image) for image in images]
	printout = _Printout(images, options)
	printout2 = _Printout(images, options)
	preview = wx.PrintPreview(printout, printout2, data)

	if not preview.Ok():
		return

	pfrm = wx.PreviewFrame(preview, parent, _('Print preview'), size=(800, 600))
	pfrm.Initialize()
	pfrm.Center()
	pfrm.Show(True)


# vim: encoding=utf8: ff=unix:
