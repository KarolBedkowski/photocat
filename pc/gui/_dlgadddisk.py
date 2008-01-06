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

__all__			= ['DlgAddDisk']


if __name__ == '__main__':
	import sys
	reload(sys)
	try:
		sys.setappdefaultencoding("utf-8")
	except:
		sys.setdefaultencoding("utf-8")
	sys.path.append('../../')

import sys
import os

import gettext
_ = gettext.gettext

import wx

from kpylibs.appconfig		import AppConfig
from kpylibs.dialogs		import message_box_error
from kpylibs.validators		import MyValidator, validators



class DlgAddDisk(wx.Dialog):
	''' Dialog dodania/uaktualnienia dysku '''

	def __init__(self, parent, data, update=False, catalog=None):
		caption = update and _('Add disk') or _('Update disk')
		wx.Dialog.__init__(self, parent, -1, caption)
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)

		self._data = data
		self.__load_disk_names(catalog, update)

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_notebook(), 0, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.SetSize((500, -1))

		self.Centre(wx.BOTH)
		
		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)


	def _create_notebook(self):
		notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_page_main(notebook),		_('Main'))
		notebook.AddPage(self._create_page_options(notebook),	_('Options'))
		return notebook


	def _create_page_main(self, parent):
		data = self._data

		panel = wx.Panel(parent, -1)
		main_grid = wx.BoxSizer(wx.VERTICAL)

		main_grid.Add(wx.StaticText(panel, -1, _('Disk name:')), 0, wx.ALL, 5)
		self._disk_name = wx.TextCtrl(panel, -1,
				validator=MyValidator(
						data_key=(data, 'name'), 
						validators=validators.NotEmptyValidator(), 
						field=_('name')
				)
		)
		main_grid.Add(self._disk_name, 0, wx.EXPAND|wx.ALL, 5)

		main_grid.Add(wx.StaticText(panel, -1, _('Disk description:')), 0, wx.ALL, 5)
		self._disk_descr = wx.TextCtrl(panel, -1, 
				validator=MyValidator(data_key=(data, 'descr')),
				style=wx.TE_MULTILINE
		)
		main_grid.Add(self._disk_descr, 1, wx.EXPAND|wx.ALL, 5)

		last_dirs, last_dir = self.__get_last_dirs()

		main_grid.Add(wx.StaticText(panel, -1, _('Folder:')), 0, wx.ALL, 5)
		self._path = wx.ComboBox(panel, -1, last_dir, 
				validator=MyValidator(
						data_key=(data, 'path'), 
						validators=validators.NotEmptyValidator(), 
						field=_('path')
				),
				choices=last_dirs)
		
		size = self._path.GetSizeTuple()[1]
		btn_sel_dir = wx.Button(panel, -1, '...', size=(size, size))

		grid = wx.BoxSizer(wx.HORIZONTAL)
		grid.Add(self._path, 1, wx.EXPAND)
		grid.Add((5, 1))
		grid.Add(btn_sel_dir, 0, wx.ALL)
		main_grid.Add(grid, 0, wx.EXPAND|wx.ALL, 5)

		panel.SetSizerAndFit(main_grid)

		self.Bind(wx.EVT_BUTTON, self._on_btn_sel_dir, btn_sel_dir)

		return panel


	def _create_page_options(self, parent):
		data = self._data
		if not data.has_key('load_captions_txt'):			data['load_captions_txt'] = True

		panel = wx.Panel(parent, -1)
		main_grid = wx.BoxSizer(wx.VERTICAL)

		main_grid.Add(wx.CheckBox(panel, -1, _('Include empty directories'), validator=MyValidator(data_key=(data, 'include_empty'))),
				0, wx.EXPAND|wx.ALL, 5)

		main_grid.Add(wx.CheckBox(panel, -1, _('Force load files'), validator=MyValidator(data_key=(data, 'force'))),
				0, wx.EXPAND|wx.ALL, 5)

		main_grid.Add(wx.CheckBox(panel, -1, _('Load info from captions.txt'), validator=MyValidator(data_key=(data, 'load_captions_txt'))),
				0, wx.EXPAND|wx.ALL, 5)

		main_grid.Add(wx.StaticText(panel, -1, _('Skip dirs (";" - separated):')))
		main_grid.Add(wx.TextCtrl(panel, -1, validator=MyValidator(data_key=(data, 'skip_subdirs'))), 0, wx.EXPAND|wx.ALL, 5)

		panel.SetSizerAndFit(main_grid)
		return panel


	def _on_btn_sel_dir(self, evt):
		curr_dir = self._path.GetValue()
		if curr_dir is None or len(curr_dir) == 0 or not os.path.exists(curr_dir) or not os.path.isdir(curr_dir):
			curr_dir = os.path.abspath(os.curdir)

		dialog = wx.DirDialog(self, _('Select directory'), defaultPath=curr_dir, style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)

		if dialog.ShowModal() == wx.ID_OK:
			directory = dialog.GetPath()
			self._path.SetValue(directory)

		dialog.Destroy()


	def _on_ok(self, evt):
		if not self.Validate():
			return

		if not self.TransferDataFromWindow():
			return

		name = self._data['name']

		if self._catalog_disk_names is not None and name in self._catalog_disk_names:
			message_box_error(self, _('Name already exists in catalog!'), _('Add disk'))
			return

		current_path  = self._data['path']

		if not os.path.exists(current_path):
			message_box_error(self, _("Selected dir don't exists!"), _('Add disk'))
			return

		last_dirs = [ current_path ] + [ path
				for path in ( self._path.GetString(idx) for idx in xrange(min(self._path.GetCount(), 9)) )
				if path != current_path
		]

		if __name__ != '__main__':
			AppConfig().set_items('add_disk-last_dir', 'last_dir', last_dirs)


		self._data['skip_dirs_list'] = [ dir.strip() for dir in self._data['skip_subdirs'].split(';') ]

		self.EndModal(wx.ID_OK)


	def __get_last_dirs(self):
		last_dir = ''
		if __name__ == '__main__':
			last_dirs = []
		else:
			last_dirs = AppConfig().get_items('add_disk-last_dir') or []
			if len(last_dirs) > 0:
				last_dirs = [ val for key, val in sorted(last_dirs) ]
				last_dir = last_dirs[0]
		return (last_dirs, last_dir)


	def __load_disk_names(self, catalog, update):
		self._catalog_disk_names = None
		if catalog is not None:
			if update:
				name = self._data['name']
				self._catalog_disk_names = tuple( ( disk.name for disk in catalog.disks if disk.name != name) )
			else:
				self._catalog_disk_names = tuple( ( disk.name for disk in catalog.disks ) )




if __name__ == '__main__':
	app = wx.PySimpleApp()
	data = {
			'name' : '__name__',
			'descr': '__descr__'
	}
	wnd = DlgAddDisk(None, data)
	if wnd.ShowModal() == wx.ID_OK:
		print 'OK', data
	else:
		print 'cancel'
	wnd.Destroy()

	del app



# vim: encoding=utf8: ff=unix:
