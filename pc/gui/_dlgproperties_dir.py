#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
 Photo Catalog v 1.x  (pc)
 Copyright (c) Karol Będkowski, 2004-2009

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

__all__			= ['DlgPropertiesDir']


import sys
import os
import time
import cStringIO

import wx
from wx.lib import masked

from kpylibs.guitools	import create_button
from kpylibs.appconfig	import AppConfig

from pc.model			import Catalog, Directory, Disk, FileImage
from components.tags_list_box import TagsListBox

_ = wx.GetTranslation


_LABEL_FONT_STYLE = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
_LABEL_FONT_STYLE.SetWeight(wx.FONTWEIGHT_BOLD)

def _creata_label(parent, title):
	ctr = wx.StaticText(parent, -1, title)
	ctr.SetFont(_LABEL_FONT_STYLE)
	return ctr



class DlgPropertiesDir(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent, item):
		wx.Dialog.__init__(self, parent, -1, _('Properties'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

		self._item = item

		self._tc_name = None

		# lista zmienionych podczas edycji nazw tagów
		self.changed_tags		= None
		self.readonly = item.catalog.readonly

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_notebook(), 1, wx.EXPAND|wx.ALL, 12)

		if self.readonly:
			main_grid.Add(self.CreateStdDialogButtonSizer(wx.CANCEL), 0, wx.EXPAND|wx.ALL, 12)

		else:
			main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 12)

		self.SetSizerAndFit(main_grid)

		appconfig = AppConfig()
		size = appconfig.get('properties_folder_wnd', 'size', (300, 300))
		self.SetSize(size)

		position = appconfig.get('properties_folder_wnd', 'position')
		if position is None:
			self.Centre(wx.BOTH)

		else:
			self.Move(position)

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self._on_close, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_CLOSE, self._on_close)


	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_layout_page_main(notebook),	_('Main'))
		notebook.AddPage(self._create_layout_page_desc(notebook),	_('Comment'))
		notebook.AddPage(self._create_layout_page_tags(notebook),	_('Tags'))
		return notebook


	def _create_layout_page_main(self, parent):
		panel = wx.Panel(parent, -1)
		sizer = wx.BoxSizer(wx.VERTICAL)

		bsizer = wx.FlexGridSizer(2, 2, 5, 12)
		bsizer.AddGrowableCol(1)

		for dummy, key, val in sorted(self._item.info):
			if key == '':
				bsizer.Add((1,5))
				bsizer.Add((1,5))

			else:
				bsizer.Add(_creata_label(panel, key + ":"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
				bsizer.Add(wx.StaticText(panel, -1, str(val)), 1, wx.EXPAND)

		sizer.Add(bsizer, 1, wx.ALL|wx.ALIGN_CENTER, 12)
		panel.SetSizerAndFit(sizer)
		return panel


	def _create_layout_page_desc(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(_creata_label(panel, _("Comment")))

		textctrl = self._textctrl_desc = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
		textctrl.SetEditable(not self.readonly)
		textctrl.SetValue(str(self._item.desc or ''))

		sizer.Add(textctrl, 1, wx.EXPAND|wx.LEFT|wx.TOP, 12)

		panel_sizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)

		return panel


	def _create_layout_page_tags(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(_creata_label(panel, _("Tags")))

		self._tags_listbox = TagsListBox(panel, -1)
		item_tags = self._item.tags
		if not self.readonly:
			all_tags = self._item.disk.catalog.tags_provider.tags

		else:
			all_tags = item_tags

		self._tags_listbox.show(all_tags, item_tags)

		sizer.Add(self._tags_listbox, 1, wx.EXPAND|wx.ALL, 12)

		panel_sizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)
		return panel


	#########################################################################


	def _on_ok(self, evt):
		item		= self._item
		changed		= False

		new_desc		= self._textctrl_desc.GetValue().strip()
		changed_desc	= (new_desc != '') if (item.desc is None) else (new_desc != item.desc)

		if changed_desc:
			item.desc	= new_desc
			changed		= True

		new_tags = self._tags_listbox.selected
		item_tags = item.tags
		changed_tags = sorted(item_tags or []) != sorted(new_tags or [])

		if changed_tags:
			self.changed_tags	= item.set_tags(new_tags)
			changed				= True

		self._on_close()

		if changed:
			self.EndModal(wx.ID_OK)

		else:
			self.EndModal(wx.ID_CANCEL)


	def _on_close(self, evt=None):
		appconfig = AppConfig()
		appconfig.set('properties_folder_wnd', 'size',		self.GetSizeTuple())
		appconfig.set('properties_folder_wnd', 'position',	self.GetPositionTuple())

		if evt is not None:
			evt.Skip()



# vim: encoding=utf8:
