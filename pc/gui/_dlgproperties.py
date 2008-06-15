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
__revision__	= '$Id$'

__all__			= ['DlgProperties']


import sys
import os
import time

import wx
from wx.lib import masked

from kpylibs.guitools	import create_button
from kpylibs.appconfig	import AppConfig

from pc.model			import Catalog, Directory, Disk, FileImage

_ = wx.GetTranslation



class DlgProperties(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent, item):
		wx.Dialog.__init__(self, parent, -1, _('Properties'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

		self._item = item
		self._item_is_fake		= is_fake = item.name is None
		self._item_is_folder	= isinstance(item, Directory)	and not is_fake
		self._item_is_disk		= isinstance(item, Disk)		and not is_fake
		self._item_is_catalog	= isinstance(item, Catalog) 	and not is_fake
		self._item_is_image		= isinstance(item, FileImage)	and not is_fake
		
		# lista zmienionych podczas edycji nazw tagów
		self.changed_tags		= None

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_notebook(), 1, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)

		appconfig = AppConfig()
		size = appconfig.get('properties_wnd', 'size', (500, 300))
		self.SetSize(size)

		position = appconfig.get('properties_wnd', 'position')
		if position is None:
			self.Centre(wx.BOTH)
		else:
			self.Move(position)

		self._show(item)

		[ self._combobox_tags.Append(tag) for tag in item.disk.catalog.tags_provider.tags ]

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self._on_close, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_CLOSE, self._on_close)


	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		
		if not self._item_is_fake:
			notebook.AddPage(self._create_layout_page_main(notebook), 	_('Main'))
			
		notebook.AddPage(self._create_layout_page_desc(notebook),		_('Description'))
		
		if self._item_is_image:
			notebook.AddPage(self._create_layout_page_exif(notebook), 	_('Exif'))
			
		notebook.AddPage(self._create_layout_page_tage(notebook),		_('Tags'))
		
		if self._item_is_image or self._item_is_fake:
			notebook.AddPage(self._create_layout_page_other(notebook),		_('Other'))
		
		return notebook


	def _create_layout_page_main(self, parent):
		panel = wx.Panel(parent, -1)

		sizer = wx.BoxSizer(wx.VERTICAL)

		if self._item_is_disk:
			name_sizer = wx.BoxSizer(wx.HORIZONTAL)
			name_sizer.Add(wx.StaticText(panel, -1, _('Name:')))
			name_sizer.Add((5, 5))
			self._tc_name = wx.TextCtrl(panel, -1)
			name_sizer.Add(self._tc_name, 1, wx.EXPAND)
			sizer.Add(name_sizer, 0, wx.EXPAND|wx.ALL, 5)

		listctrl = self._listctrl_main = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_NO_HEADER)
		sizer.Add(listctrl, 1, wx.EXPAND|wx.ALL, 5)
		panel.SetSizerAndFit(sizer)

		listctrl.InsertColumn(0, '')
		listctrl.InsertColumn(1, '')

		return panel


	def _create_layout_page_desc(self, parent):
		panel = wx.Panel(parent, -1)

		textctrl = self._textctrl_desc = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)

		sizer = wx.BoxSizer(wx.VERTICAL)

		if self._item_is_fake:
			self._cb_set_descr = wx.CheckBox(panel, -1, _('Set description'))
			sizer.Add(self._cb_set_descr, 0, wx.EXPAND|wx.ALL, 5)

		sizer.Add(textctrl,1, wx.EXPAND|wx.ALL, 5)
		panel.SetSizerAndFit(sizer)

		return panel


	def _create_layout_page_exif(self, parent):
		panel = wx.Panel(parent, -1)

		listctrl = self._listctrl_exif = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(listctrl, 1, wx.EXPAND|wx.ALL, 5)
		panel.SetSizerAndFit(sizer)

		listctrl.InsertColumn(0, _('Tag'))
		listctrl.InsertColumn(1, _('Value'))

		return panel


	def _create_layout_page_tage(self, parent):
		panel = wx.Panel(parent, -1)

		sizer = wx.BoxSizer(wx.VERTICAL)
		
		if self._item_is_fake:
			self._cb_set_tags = wx.CheckBox(panel, -1, _('Set tags'))
			sizer.Add(self._cb_set_tags, 0, wx.EXPAND|wx.ALL, 5)

		listbox = self._listbox_tags = wx.ListBox(panel, -1, style=wx.LB_SINGLE)
		sizer.Add(listbox, 1, wx.EXPAND|wx.ALL, 5)

		subsizer = wx.BoxSizer(wx.HORIZONTAL)
		
		combobox = self._combobox_tags = wx.ComboBox(panel, -1, style=wx.CB_SORT)
		subsizer.Add(combobox, 1, wx.EXPAND|wx.ALL, 2)
		
		button1	= create_button(panel, _('Add'), self._on_add_tag)		
		subsizer.Add(button1, 0, wx.EXPAND|wx.ALL, 2)
		
		button2	= create_button(panel, _('Del'), self._on_del_tag)
		subsizer.Add(button2, 0, wx.EXPAND|wx.ALL, 2)

		sizer.Add(subsizer, 0, wx.EXPAND|wx.ALL, 5)

		panel.SetSizerAndFit(sizer)

		return panel
	

	def _create_layout_page_other(self, parent):
		panel = wx.Panel(parent, -1)		
		sizer = wx.BoxSizer(wx.VERTICAL)

		subsizer = wx.BoxSizer(wx.HORIZONTAL)
		self._cb_shot_date = wx.CheckBox(panel, 1, _("Shot date:"))
		subsizer.Add(self._cb_shot_date, 0, wx.EXPAND|wx.ALL, 5)
		
		self._dp_shot_date = wx.DatePickerCtrl(panel , size=(120, -1),
				style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.SUNKEN_BORDER)		
		subsizer.Add(self._dp_shot_date, 0, wx.EXPAND, wx.EXPAND|wx.ALL, 5)
		
		self._tc_shot_time = masked.TimeCtrl(panel , -1, fmt24hr=True)
		subsizer.Add(self._tc_shot_time, 0, wx.EXPAND, wx.EXPAND|wx.ALL, 5)
		
		sizer.Add(subsizer, 0, wx.EXPAND|wx.ALL, 5)
		panel.SetSizerAndFit(sizer)

		self.Bind(wx.EVT_CHECKBOX, self._on_checkbox_short_date, self._cb_shot_date)
		
		return panel


	#########################################################################


	def _show(self, item):
		if self._item_is_disk:
			self._tc_name.SetValue(item.name)

		if not self._item_is_fake:
			listctrl = self._listctrl_main

			def insert(key, val):
				idx = listctrl.InsertStringItem(sys.maxint, str(key))
				listctrl.SetStringItem(idx, 1, str(val))

			[ insert(key, val) for dummy, key, val in sorted(item.info) ]

			listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
			listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

		self._textctrl_desc.SetValue(str(item.desc or ''))

		if self._item_is_image:
			listctrl = self._listctrl_exif
			exif = item.exif_data
			if exif is not None:
				for key, val in sorted(exif.iteritems()):
					idx = listctrl.InsertStringItem(sys.maxint, str(key))
					listctrl.SetStringItem(idx, 1, str(val))

				listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
				listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

		if item.tags is not None:
			listbox = self._listbox_tags
			[ listbox.Append(tag) for tag in item.tags ]

		if self._item_is_image:
			shot_date_present = item.shot_date is not None and item.shot_date > 0
			self._cb_shot_date.SetValue(shot_date_present)
			self._dp_shot_date.Enable(shot_date_present)
			self._tc_shot_time.Enable(shot_date_present)
			if shot_date_present:
				date = wx.DateTime()
				date.SetTimeT(item.shot_date)
				self._dp_shot_date.SetValue(date)
				self._tc_shot_time.SetValue(date)
		elif self._item_is_fake:
			self._cb_shot_date.SetValue(False)
			self._dp_shot_date.Enable(False)
			self._tc_shot_time.Enable(False)
			

	#########################################################################


	def _on_ok(self, evt):
		item = self._item

		changed = False

		if self._item_is_disk:
			new_name = self._tc_name.GetValue().strip() or item.name
			changed = item.name != new_name
			item.name  =  new_name

		if not self._item_is_fake or self._cb_set_descr.IsChecked():
			new_desc = self._textctrl_desc.GetValue().strip()
			if item.desc is None:
				changed_desc = new_desc != ''
			else:
				changed_desc = new_desc != item.desc
			if changed_desc:
				item.desc = new_desc
				changed = True
		else:
			item.desc = None

		if not self._item_is_fake or self._cb_set_tags.IsChecked():
			listbox = self._listbox_tags
			tag_iter = ( listbox.GetString(idx).strip() for idx in xrange(listbox.GetCount()) )
			tags = tuple(sorted([ tag for tag in tag_iter if len(tag) > 0 ]))
			if item.tags is None:
				changed_tags = len(tags) > 0
			else:
				changed_tags = tags != item.tags
			if changed_tags:
				self.changed_tags = item.set_tags(tags)
				changed = True
		else:
			item.tags = None
			
		if self._item_is_image or self._item_is_fake:
			if self._cb_shot_date.IsChecked():
				sdate = self._dp_shot_date.GetValue()
				stime = self._tc_shot_time.GetValue(as_wxDateTime=True)
				sdate.SetHour(stime.GetHour())
				sdate.SetMinute(stime.GetMinute())
				sdate.SetSecond(stime.GetSecond())
				sdate_val = sdate.GetTicks()
				if item.shot_date is None or item.shot_date != sdate_val:
					item.shot_date = sdate_val
					changed = True
			elif item.shot_date is not None:
				item.shot_date = None
				changed = True

		self._on_close()
		if changed:
			self.EndModal(wx.ID_OK)
		else:
			self.EndModal(wx.ID_CANCEL)


	def _on_add_tag(self, evt):
		tag = self._combobox_tags.GetValue().strip()
		if len(tag) > 0:
			tag = tag.lower()
			listbox = self._listbox_tags
			tags = [ listbox.GetString(idx) for idx in xrange(listbox.GetCount()) ]
			if tags.count(tag) == 0:
				listbox.Append(tag)
				self._combobox_tags.Append(tag)


	def _on_del_tag(self, evt):
		sel = self._listbox_tags.GetSelection()
		if sel >=0 :
			self._listbox_tags.Delete(sel)


	def _on_close(self, evt=None):
		appconfig = AppConfig()
		appconfig.set('properties_wnd', 'size',		self.GetSizeTuple())
		appconfig.set('properties_wnd', 'position',	self.GetPositionTuple())

		if evt is not None:
			evt.Skip()

	
	def _on_checkbox_short_date(self, evt):
		value = evt.IsChecked()
		self._dp_shot_date.Enable(value)
		self._tc_shot_time.Enable(value)


# vim: encoding=utf8:
