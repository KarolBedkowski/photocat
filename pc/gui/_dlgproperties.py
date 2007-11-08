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
import os
import time

import gettext
_ = gettext.gettext

import wx

from kpylibs.guitools	import create_button

from pc.model.catalog		import Catalog
from pc.model.folder		import Folder
from pc.model.disc			import Disc
from pc.model.image			import Image


class DlgProperties(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent, item):
		wx.Dialog.__init__(self, parent, -1, _('Properties'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)
		
		self._item = item

		self._is_fake = is_fake = item.name is None
		
		self._item_is_folder	= isinstance(item, Folder)	and not is_fake
		self._item_is_disc		= isinstance(item, Disc)	and not is_fake
		self._item_is_catalog	= isinstance(item, Catalog) and not is_fake
		self._item_is_image		= isinstance(item, Image)	and not is_fake

		
		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_notebook(), 1, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.SetSize((500, 300))

		self.Centre(wx.BOTH)
		
		self._show(item)
		
		[ self._combobox_tags.Append(tag) for tag in item.catalog.tags_provider.tags ] 
		
		wx.EVT_BUTTON(self, wx.ID_OK, self._on_ok)


	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		if not self._is_fake:
			notebook.AddPage(self._create_layout_page_main(notebook), 	_('Main'))
		notebook.AddPage(self._create_layout_page_desc(notebook), 	_('Description'))
		if self._item_is_image:
			notebook.AddPage(self._create_layout_page_exif(notebook), 	_('Exif'))
		notebook.AddPage(self._create_layout_page_tage(notebook), 	_('Tags'))
		return notebook


	def _create_layout_page_main(self, parent):
		panel = wx.Panel(parent, -1)
		listctrl = self._listctrl_main = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(listctrl, 1, wx.EXPAND)
		panel.SetSizerAndFit(sizer)
		
		listctrl.InsertColumn(0, 'Tag')
		listctrl.InsertColumn(1, 'Value')
		
		return panel
		
		
	def _create_layout_page_desc(self, parent):
		panel = wx.Panel(parent, -1)
		
		textctrl = self._textctrl_desc = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(textctrl,1, wx.EXPAND|wx.ALL, 5)
		panel.SetSizerAndFit(sizer)
		
		return panel
		
		
	def _create_layout_page_exif(self, parent):
		panel = wx.Panel(parent, -1)
		
		listctrl = self._listctrl_exif = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(listctrl, 1, wx.EXPAND)
		panel.SetSizerAndFit(sizer)
		
		listctrl.InsertColumn(0, 'Tag')
		listctrl.InsertColumn(1, 'Value')
		
		return panel


	def _create_layout_page_tage(self, parent):
		panel = wx.Panel(parent, -1)
		
		listbox = self._listbox_tags = wx.ListBox(panel, -1, style=wx.LB_SINGLE)
		combobox = self._combobox_tags = wx.ComboBox(panel, -1, style=wx.CB_SORT)
		button1	= create_button(panel, _('Add'), self._on_add_tag)
		button2	= create_button(panel, _('Del'), self._on_del_tag)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(listbox, 1, wx.EXPAND)
		
		subsizer = wx.BoxSizer(wx.HORIZONTAL)
		subsizer.Add(combobox, 1, wx.EXPAND)
		subsizer.Add(button1, 0, wx.EXPAND)
		subsizer.Add(button2, 0, wx.EXPAND)
		
		sizer.Add(subsizer, 0, wx.EXPAND)
		
		panel.SetSizerAndFit(sizer)
		
		return panel
		
		
	def _show(self, item):
		if not self._is_fake:
			listctrl = self._listctrl_main
			
			def insert(key, val):
				idx = listctrl.InsertStringItem(sys.maxint, str(key))
				listctrl.SetStringItem(idx, 1, str(val))
				
			insert(_('Name'),	item.name)
			insert(_('Size'),	item.size)
			insert(_('Date'),	time.asctime(time.localtime(item.date)))
				
			listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
			listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

		self._textctrl_desc.SetValue(str(item.descr or ''))

		if self._item_is_image:
			listctrl = self._listctrl_exif
			for key, val in sorted(item.exif.items()):
				idx = listctrl.InsertStringItem(sys.maxint, str(key))
				listctrl.SetStringItem(idx, 1, str(val))
				
			listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
			listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
			
		listbox = self._listbox_tags
		[ listbox.Append(tag) for tag in item.tags ] 
			
			
	def _on_ok(self, evt):
		item = self._item
		item.descr = self._textctrl_desc.GetValue()
		listbox = self._listbox_tags
		tag_iter = ( listbox.GetString(idx).strip() for idx in xrange(listbox.GetCount()) )
		tags = [ tag for tag in tag_iter if len(tag) > 0 ]
		item.set_tags(tags)
		self.EndModal(wx.ID_OK)
		
		
	def _on_add_tag(self, evt):
		tag = self._combobox_tags.GetValue().strip()
		if len(tag) > 0:
			tag = tag.lower()
			listbox = self._listbox_tags
			tags = [ listbox.GetString(idx) for idx in xrange(listbox.GetCount()) ]
			if tags.count(tag) > 0:
				return
			listbox.Append(tag)
			self._combobox_tags.Append(tag)


	def _on_del_tag(self, evt):
		sel = self._listbox_tags.GetSelection()
		if sel >=0 :
			self._listbox_tags.Delete(sel)

# vim: encoding=utf8:
