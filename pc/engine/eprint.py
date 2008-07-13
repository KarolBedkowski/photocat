#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
pc.engine.eprint
 -- engine do obsługi drukowania

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

import wx

from pc.gui.components._thumb import Thumb

from thumb_drawer import ThumbDrawer

_ = wx.GetTranslation



class _Printout(wx.Printout):
	def __init__(self, items, options):
		wx.Printout.__init__(self)
		self.items			= items
		self.drawer			= ThumbDrawer(self)
		self._num_pages		= 0
		self._items_per_page = []
		self._options		= options

		self.drawer.set_captions_font(options['fontdata'])
		self.drawer.thumb_width		= options['thumb_width']
		self.drawer.thumb_height	= options['thumb_height']
		self.drawer.show_captions	= options['show_captions']
		self.drawer.group_by_date	= options['group_by_date']


	def _calc_scale(self, dc):
		ppiPrinterX, ppiPrinterY	= self.GetPPIPrinter()
		ppiScreenX, ppiScreenY		= self.GetPPIScreen()
		log_scale					= float(ppiPrinterX) / float(ppiScreenX)

		pw, ph	= self.GetPageSizePixels()
		dw, dh	= dc.GetSize()
		scale	= log_scale * float(dw) / float(pw)

		dc.SetUserScale(scale, scale)
		self._log_units_mm = float(ppiPrinterX) / (log_scale * 25.4)


	def _calc_layout(self, dc):
		x1, x2, y1, y2 = 5, 5, 5, 5

		dw, dh = dc.GetSize()
		px1 = x1 * self._log_units_mm
		py1 = y1 * self._log_units_mm
		px2 = dc.DeviceToLogicalXRel(dw) - x2 * self._log_units_mm
		py2 = dc.DeviceToLogicalYRel(dh) - y2 * self._log_units_mm

		page_height = int(py2 - py1)
		page_width	= int(px2 - px1)

		dc.SetDeviceOrigin(x1, y1)

		# rysowanie marginesów
		#dc.DrawRectangleRect(wx.RectPP((x1, y1), (page_width-x2, page_height-y2)))

		return page_width, page_height


	def HasPage(self, page):
		return page <= self._num_pages

	def GetPageInfo(self):
		return (1, self._num_pages, 1, self._num_pages)


	def OnPrintPage(self, page):
		dc = self.GetDC()

		self._calc_scale(dc)
		width, height = self._calc_layout(dc)

		res		= self.drawer.update(self._items_per_page[page-1], width, height, dc=dc)
		cols, rows, virtual_size, size_hints, scroll_rate, last_index = res

		self.drawer.draw(dc, None)

		return True


	def OnPreparePrinting(self):
		dc = self.GetDC()
		self._calc_scale(dc)
		width, height = self._calc_layout(dc)

		begin = 0
		last_index = -1
		self._num_pages = 0
		self._items_per_page = []
		while True:
			res		= self.drawer.update(self.items[begin:], width, height, dc=dc)
			last_index = res[5]

			if last_index == 0:
				break

			self._items_per_page.append(self.items[begin:begin+last_index])
			begin += last_index
			self._num_pages += 1


	def GetBackgroundColour(self):
		return wx.WHITE




def print_preview(parent, print_data, images, options):
	data = wx.PrintDialogData(print_data)

	images = [ Thumb(image) for image in images ]

	printout = _Printout(images, options)
	printout2 = _Printout(images, options)
	preview = wx.PrintPreview(printout, printout2, data)

	if not preview.Ok():
		return

	pfrm = wx.PreviewFrame(preview, parent, _('Print preview'))
	pfrm.Initialize()
	pfrm.Show(True)


# vim: encoding=utf8: ff=unix:
