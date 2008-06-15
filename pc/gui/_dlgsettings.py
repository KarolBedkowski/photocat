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

__all__			= ['DlgSettings']


import sys
import os
import time

import wx
from wx.lib import masked

from kpylibs.guitools	import create_button
from kpylibs.appconfig	import AppConfig
from kpylibs.validators	import MyValidator, validators

from pc.model			import Catalog, Directory, Disk, FileImage

_ = wx.GetTranslation

_SETTINGS_KEYS = (
		('thumb_width', 200), ('thumb_height', 200), ('thumb_compression', 50),
		('view_preload', True), ('view_show_captions', True)
)



class DlgSettings(wx.Dialog):
	''' Dialog ustawień programu '''

	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, _('Program settings'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)

		self._data = self._load_settings()
		
		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_notebook(), 1, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self._on_close, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_CLOSE, self._on_close)


	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_layout_page_thumbs(notebook),		_('Thumbs'))
		notebook.AddPage(self._create_layout_page_view(notebook),		_('View'))
		return notebook


	def _create_layout_page_thumbs(self, parent):
		panel = wx.Panel(parent, -1)

		grid = wx.BoxSizer(wx.HORIZONTAL)

		sizer = wx.FlexGridSizer(2, 2, 5, 5)

		def add(label, control):
			sizer.Add(wx.StaticText(panel, -1, label), 0, wx.LEFT|wx.TOP, 2)
			sizer.Add(control, 1, wx.EXPAND)
			return control

		self._tc_thumb_width = add(_('Thumb width:'), masked.NumCtrl(panel, -1,
				integerWidth=3, allowNegative=False, min=50, max=500,
				validator=MyValidator(data_key=(self._data, 'thumb_width'))
		))

		self._tc_thumb_height = add(_('Thumb height:'), masked.NumCtrl(panel, -1,
				integerWidth=3, allowNegative=False, min=50, max=500,
				validator=MyValidator(data_key=(self._data, 'thumb_height'))
		))

		self._tc_thumb_compression = add(_('Compression:'), masked.NumCtrl(panel, -1,
				integerWidth=3, allowNegative=False, min=20, max=100,
				validator=MyValidator(data_key=(self._data, 'thumb_compression'))
		))
		
		grid.Add(sizer, 1, wx.EXPAND|wx.ALL, 5)

		panel.SetSizerAndFit(grid)
		return panel
	

	def _create_layout_page_view(self, parent):
		panel = wx.Panel(parent, -1)
		
		grid = wx.BoxSizer(wx.VERTICAL)

		self._tc_thumb_preload = wx.CheckBox(panel, -1, _('Thumb preload'),
				validator=MyValidator(data_key=(self._data, 'view_preload'))
		)
		grid.Add(self._tc_thumb_preload, 0, wx.EXPAND|wx.ALL, 5)

		self._tc_thumb_captions = wx.CheckBox(panel, -1, _('Show captions'), 
				validator=MyValidator(data_key=(self._data, 'view_show_captions'))
		)
		grid.Add(self._tc_thumb_captions, 0, wx.EXPAND|wx.ALL, 5)

		panel.SetSizerAndFit(grid)
		
		return panel

	#########################################################################


	def _on_ok(self, evt):
		if not self.Validate():
			return

		if not self.TransferDataFromWindow():
			return

		if self._data['thumb_height'] < 25 or self._data['thumb_height'] > 500:			
			self._data['thumb_height'] = 200

		if self._data['thumb_width'] < 25 or self._data['thumb_width'] > 500:
			self._data['thumb_width'] = 200

		if self._data['thumb_compression'] < 10 or self._data['thumb_compression'] > 100:
			self._data['thumb_compression'] = 50

		self._save_settings()
		self.EndModal(wx.ID_OK)


	def _on_close(self, evt=None):
		if evt is not None:
			evt.Skip()


	#########################################################################


	def _load_settings(self):
		appconfig = AppConfig()
		data = dict(_SETTINGS_KEYS)
		for key, val in appconfig.get_items('settings') or []:
			data[key] = val
		return data


	def _save_settings(self):
		appconfig = AppConfig()
		data = self._data
		for key, default in data.iteritems():
			appconfig.set('settings', key, data[key])


# vim: encoding=utf8:
