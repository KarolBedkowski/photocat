#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
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
__revision__	= '$Id: _dlgabout.py 2 2006-12-24 21:07:13Z k $'

__all__			= ['DlgProperties']


import sys

import gettext
_ = gettext.gettext

import wx

from kpylibs.guitools		import create_button
from kpylibs.iconprovider	import IconProvider
from kpylibs.appconfig		import AppConfig

from pc.model.catalog		import Catalog
from pc.model.folder		import Folder
from pc.model.disc			import Disc
from pc.model.image			import Image



class DlgSearch(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent, catalogs):
		wx.Dialog.__init__(self, parent, -1, _('Find'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)
		
		self._catalogs	= catalogs
		self._parent	= parent
		self._result	= []
		
		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['image', 'folder1'])
		
		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_fields(),	0, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self._create_layout_list(),	1, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.SetSize((500, 300))

		self.Centre(wx.BOTH)


	def _create_layout_fields(self):
		grid = wx.FlexGridSizer(1, 3, 2, 2)
		grid.AddGrowableCol(1)
		grid.Add(wx.StaticText(self, -1, _('Text')), 0, wx.EXPAND|wx.ALL, 5)
		
		last = AppConfig().get_items('last_search')
		if last is None:
			last = []
		else:
			last = [l[1] for l in last]
		
		self._tc_text = wx.ComboBox(self, -1, choices=last)
		grid.Add(self._tc_text, 1, wx.EXPAND)
		grid.Add(create_button(self, _('Find'), self._on_btn_find), 0, wx.EXPAND)
		return grid
	

	def _create_layout_list(self):
		listctrl = self._result_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
		listctrl.SetImageList(self._icon_provider.get_image_list(), wx.IMAGE_LIST_SMALL)
		listctrl.InsertColumn(0, _('Name'))
		listctrl.InsertColumn(1, _('Path'))
		
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_activate, listctrl)
		
		return listctrl
	

	def _on_btn_find(self, evt):
		what = self._tc_text.GetValue().strip()
		if len(what) == 0:
			return
		
		last_search_text_ctrl = self._tc_text
		
		if len([ None
				for idx
				in xrange(last_search_text_ctrl.GetCount())
				if last_search_text_ctrl.GetString(idx) == what ]) == 0:
			last_search_text_ctrl.Insert(0, what)
			
			
		last = [ last_search_text_ctrl.GetString(idx) for idx in xrange(min(last_search_text_ctrl.GetCount(), 10)) ]
		AppConfig().set_items('last_search', 'text', last)
		
		listctrl = self._result_list
		listctrl.DeleteAllItems()

		icon_folder_idx = self._icon_provider.get_image_index('folder1')
		icon_image_idx = self._icon_provider.get_image_index('image')
		
		self._result = []

		def insert(item):
			if isinstance(item, Image):
				ico = icon_image_idx
			else:
				ico = icon_folder_idx
			idx = listctrl.InsertImageStringItem(sys.maxint, str(item.name), ico)
			listctrl.SetStringItem(idx, 1, item.path)
			listctrl.SetItemData(idx, len(self._result))
			self._result.append(item)

		for catalog in self._catalogs:
			result = catalog.check_on_find(what)
			for item in result:
				insert(item)

		listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		
		
	def _on_list_activate(self, evt):
		listctrl = self._result_list
		if listctrl.GetSelectedItemCount() > 0:
			index	= listctrl.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			itemidx	= listctrl.GetItemData(index)
			item	= self._result[itemidx]
			if isinstance(item, Folder) or isinstance(item, Disc):
				self._parent.show_item(item)
			elif isinstance(item, Image):
				self._parent.show_item(item.parent)
			
			

# vim: encoding=utf8: ff=unix: