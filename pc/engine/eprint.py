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

_ = wx.GetTranslation



class _Printout(wx.Printout):
	def __init__(self, canvas):
		wx.Printout.__init__(self)
		self.canvas = canvas


	def OnPrintPage(self, page):
		dc = self.GetDC()

		#-------------------------------------------
		# One possible method of setting scaling factors...

		maxX, maxY = self.canvas.GetClientSizeTuple()

		# Let's have at least 50 device units margin
		marginX = 50
		marginY = 50

		# Add the margin to the graphic size
		maxX = maxX + (2 * marginX)
		maxY = maxY + (2 * marginY)

		# Get the size of the DC in pixels
		(w, h) = dc.GetSizeTuple()

		# Calculate a suitable scaling factor
		scaleX = float(w) / maxX
		scaleY = float(h) / maxY

		# Use x or y scaling factor, whichever fits on the DC
		actualScale = min(scaleX, scaleY)

		width, height = self.canvas.GetClientSizeTuple()

		# Calculate the position on the DC for centering the graphic
		posX = (w - (width * actualScale)) / 2.0
		posY = (h - (height * actualScale)) / 2.0

		# Set the scale and origin
		dc.SetUserScale(actualScale, actualScale)
		dc.SetDeviceOrigin(int(posX), int(posY))

		#-------------------------------------------

		self.canvas.draw(dc, None)
		dc.DrawText("Page: %d" % page, marginX/2, maxY-marginY)

		return True




def print_preview(parent, print_data, canvas):
	data = wx.PrintDialogData(print_data)
	printout = _Printout(canvas)
	printout2 = _Printout(canvas)
	preview = wx.PrintPreview(printout, printout2, data)

	if not preview.Ok():
		return

	pfrm = wx.PreviewFrame(preview, parent, _('Print preview'))
	pfrm.Initialize()
	pfrm.Show(True)


# vim: encoding=utf8: ff=unix:
