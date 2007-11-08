#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
 SAG - Simple Album Generator 3.x  (sag3)
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

 This file is part of Simple Album Generator (SAG)

 SAG is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 SAG is distributed in the hope that it will be useful, but WITHOUT ANY
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

__all__			= ['DlgAddDisc']

import sys
import os

import gettext
_ = gettext.gettext

import wx

from kpylibs.appconfig		import AppConfig
from kpylibs.dialogs		import message_box_error



class DlgAddDisc(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, _('Add disc'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

		main_grid = wx.BoxSizer(wx.VERTICAL)
		
		main_grid.Add(wx.StaticText(self,-1, _('Disc name:')), 0, wx.ALL, 5)
		self._disc_name = wx.TextCtrl(self, -1)
		main_grid.Add(self._disc_name, 0, wx.EXPAND|wx.ALL, 5)
		
		main_grid.Add(wx.StaticText(self,-1, _('Disc description:')), 0, wx.ALL, 5)
		self._disc_descr = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
		main_grid.Add(self._disc_descr, 1, wx.EXPAND|wx.ALL, 5)
		
		main_grid.Add(wx.StaticText(self,-1, _('Folder:')), 0, wx.ALL, 5)
		
		last_dir = AppConfig().get('add_disc', 'last_dir') or ''
		
		self._path = wx.TextCtrl(self, -1, last_dir)
		btn_sel_dir = wx.Button(self, -1, '...')
		
		grid = wx.BoxSizer(wx.HORIZONTAL)
		grid.Add(self._path, 1, wx.EXPAND)
		grid.Add(btn_sel_dir, 0, wx.ALL)
		
		main_grid.Add(grid, 0, wx.EXPAND|wx.ALL, 5)
		
		main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.SetSize((500, 300))

		self.Centre(wx.BOTH)
		
		self.Bind(wx.EVT_BUTTON, self._on_btn_sel_dir, btn_sel_dir)
		wx.EVT_BUTTON(self, wx.ID_OK, self._on_ok)
		
	
	@property
	def path(self):
		return self._path.GetValue()
								   
	@property
	def name(self):
		return self._disc_name.GetValue()
	
	@property
	def descr(self):
		return self._disc_descr.GetValue()
	

	def _on_btn_sel_dir(self, evt):
		
		curr_dir = self.path
		if curr_dir is None or len(curr_dir) == 0 or not os.path.exists(curr_dir) or not os.path.isdir(curr_dir):
			curr_dir = os.path.abspath(os.curdir)
		
		dialog = wx.DirDialog(self, _('Select directory'), defaultPath=curr_dir,
				style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
		
		if dialog.ShowModal() == wx.ID_OK:
			directory = dialog.GetPath()
			self._path.SetValue(directory)
			
		dialog.Destroy()
		
		
	def _on_ok(self, evt):
		if len(self.name) == 0:
			message_box_error(self, _('Name is empty!'), _('Add disc'))
			return
		if len(self.path) == 0:
			message_box_error(self, _('Path is empty!'), _('Add disc'))
			return
		AppConfig().set('add_disc', 'last_dir', self.path)
		self.EndModal(wx.ID_OK)


# vim: encoding=utf8: ff=unix: 