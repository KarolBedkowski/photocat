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



import wx
import wx.lib.scrolledpanel as scrolled


_ = wx.GetTranslation

_LABEL_FONT_STYLE = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
_LABEL_FONT_STYLE.SetWeight(wx.FONTWEIGHT_BOLD)



def _create_label(parent, title):
	ctr = wx.StaticText(parent, -1, title)
	ctr.SetFont(_LABEL_FONT_STYLE)
	return ctr



class InfoPanel(wx.Panel):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self._create_layout(self), 1, wx.EXPAND)
		self.SetSizerAndFit(sizer)


	def _create_layout(self, parent):
		self._panel_main = panel = scrolled.ScrolledPanel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)

		self._panel_info_main = wx.Panel(panel, -1)
		panel_sizer.Add(self._panel_info_main, 0, wx.EXPAND|wx.ALL, 12)

		panel_sizer.Add((12, 12))

		self._panel_info_exif = wx.Panel(panel, -1)
		panel_sizer.Add(self._panel_info_exif, 0, wx.EXPAND|wx.ALL, 12)

		panel.SetSizerAndFit(panel_sizer)
		return panel


	#########################################################################


	def _show_main(self, image, what):
		panel = self._panel_info_main
		panel.DestroyChildren()
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)

		subsizer = wx.BoxSizer(wx.VERTICAL)
		subsizer.Add(_create_label(panel, what), 0, wx.EXPAND|wx.BOTTOM, 5)

		bsizer = wx.FlexGridSizer(2, 2, 5, 12)
		bsizer.AddGrowableCol(1)

		for dummy, key, val in sorted(image.info):
			if key == '':
				bsizer.Add((1,5))
				bsizer.Add((1,5))

			else:
				bsizer.Add(_create_label(panel, key + ":"), 0, 
						wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
				bsizer.Add(wx.StaticText(panel, -1, str(val)), 1, wx.EXPAND)

		subsizer.Add(bsizer, 1, wx.EXPAND|wx.LEFT, 12)

		sizer.Add(subsizer)

		if image.desc:
			sizer.Add((12, 12))

			subsizer = wx.BoxSizer(wx.VERTICAL)
			subsizer.Add(_create_label(panel, _("Description")), 0, 
					wx.EXPAND|wx.BOTTOM, 5)

			st_desc = wx.TextCtrl(panel, -1, image.desc,
					style=wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
			st_desc.SetBackgroundColour(panel.GetBackgroundColour())
			subsizer.Add(st_desc, 1, wx.EXPAND|wx.LEFT, 12)
			
			sizer.Add(subsizer, 1, wx.EXPAND)

		panel.SetSizerAndFit(sizer)


	def _show_exif(self, image):
		# exif
		panel = self._panel_info_exif

		if image.exif_data is not None and len(image.exif_data) > 0:
			sizer = wx.BoxSizer(wx.VERTICAL)

			sizer.Add(_create_label(panel, _("Exif")), 0, wx.EXPAND|wx.BOTTOM, 5)

			bsizer = wx.FlexGridSizer(2, 2, 5, 12)
			bsizer.AddGrowableCol(1)

			for key, val in sorted(image.exif_data.iteritems()):
				bsizer.Add(_create_label(panel, key + ":"), 0, 
						wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
				stext = wx.StaticText(panel, -1, str(val[:100]))
				#stext = wx.TextCtrl(panel, -1, str(val), style=wx.TE_READONLY|wx.BORDER_NONE)
				bsizer.Add(stext, 1, wx.EXPAND)

			sizer.Add(bsizer, 0, wx.EXPAND|wx.LEFT, 12)
			panel.SetSizerAndFit(sizer)


	#########################################################################


	def show(self, image):
		self.Freeze()
		self.clear()
		self._show_main(image, _("File"))
		self._show_exif(image)
		self._panel_main.SetupScrolling(scroll_x=False)
		self.Thaw()


	def show_folder(self, folder):
		self.Freeze()
		self._show_main(folder, _("Directory"))
		self._panel_main.SetupScrolling(scroll_x=False)
		self.Thaw()


	def clear(self):
		panel = self._panel_info_exif
		panel.DestroyChildren()

	#########################################################################



# vim: encoding=utf8: ff=unix:
