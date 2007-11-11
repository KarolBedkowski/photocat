#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
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

	def __init__(self, parent, update=False, name=None, desc=None):
		caption = update and _('Add disc') or _('Update disc')
		wx.Dialog.__init__(self, parent, -1, caption, style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

		main_grid = wx.BoxSizer(wx.VERTICAL)

		main_grid.Add(wx.StaticText(self,-1, _('Disc name:')), 0, wx.ALL, 5)
		self._disc_name = wx.TextCtrl(self, -1, name or '')
		main_grid.Add(self._disc_name, 0, wx.EXPAND|wx.ALL, 5)

		main_grid.Add(wx.StaticText(self,-1, _('Disc description:')), 0, wx.ALL, 5)
		self._disc_descr = wx.TextCtrl(self, -1, desc or '', style=wx.TE_MULTILINE)
		main_grid.Add(self._disc_descr, 1, wx.EXPAND|wx.ALL, 5)

		main_grid.Add(wx.StaticText(self,-1, _('Folder:')), 0, wx.ALL, 5)

		last_dirs = AppConfig().get_items('add_disc-last_dir') or []
		last_dir = ''
		if len(last_dirs) > 0:
			last_dirs = [ val for key, val in sorted(last_dirs) ]
			last_dir = last_dirs[0]

		self._path = wx.ComboBox(self, -1, last_dir, choices=last_dirs)
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
		return self._path.GetValue().strip()


	@property
	def name(self):
		return self._disc_name.GetValue().strip()


	@property
	def descr(self):
		return self._disc_descr.GetValue().strip()


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

		current_path  = self.path
		last_dirs = [ current_path ]

		[ last_dirs.append(path)
				for path in ( self._path.GetString(idx) for idx in xrange(min(self._path.GetCount(), 9)) )
				if path != current_path
		]

		AppConfig().set_items('add_disc-last_dir', 'last_dir', last_dirs)
		self.EndModal(wx.ID_OK)


# vim: encoding=utf8: ff=unix:
