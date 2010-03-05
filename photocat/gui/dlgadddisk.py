#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'
__all__ = ['DlgAddDisk']


if __name__ == '__main__':
	import sys
	reload(sys)
	try:
		sys.setappdefaultencoding("utf-8")
	except:
		sys.setdefaultencoding("utf-8")
	sys.path.append('../../')

import os

import wx

from photocat.lib.appconfig import AppConfig
from photocat.lib.wxtools.dialogs import message_box_error
from photocat.lib.wxtools.validators import MyValidator, validators

_LABEL_FONT_STYLE = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
_LABEL_FONT_STYLE.SetWeight(wx.FONTWEIGHT_BOLD)

_SMALL_FONT_STYLE = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
_SMALL_FONT_STYLE.SetPointSize(_SMALL_FONT_STYLE.GetPointSize()-1)


def _create_label(parent, title):
	ctr = wx.StaticText(parent, -1, title)
	ctr.SetFont(_LABEL_FONT_STYLE)
	return ctr


def _create_small_label(parent, title):
	ctr = wx.StaticText(parent, -1, title)
	ctr.SetFont(_SMALL_FONT_STYLE)
	return ctr


class DlgAddDisk(wx.Dialog):
	''' Dialog dodania/uaktualnienia dysku '''

	def __init__(self, parent, data, update=False, collection=None):
		caption = _('Update disk') if update else _('Add disk to collection')
		wx.Dialog.__init__(self, parent, -1, caption)
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)

		self._data = data
		self.__load_disk_names(collection, update)

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_notebook(), 1, wx.EXPAND | wx.ALL, 12)
		main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL), 0,
				wx.EXPAND | wx.ALL, 12)

		self.SetSizerAndFit(main_grid)
		self.SetSize((500, -1))

		self.Centre(wx.BOTH)

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)

	def _create_notebook(self):
		notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_page_main(notebook), _('Main'))
		notebook.AddPage(self._create_page_options(notebook), _('Options'))
		return notebook

	def _create_page_main(self, parent):
		data = self._data

		panel = wx.Panel(parent, -1)
		main_grid = wx.BoxSizer(wx.VERTICAL)

		grid = wx.FlexGridSizer(3, 2, 5, 12)
		grid.AddGrowableRow(1)
		grid.AddGrowableCol(1)

		grid.Add(wx.StaticText(panel, -1, _('Disk name:')))
		self._disk_name = wx.TextCtrl(panel, -1,
				validator=MyValidator(data_key=(data, 'name'),
						validators=validators.NotEmptyValidator(),
						field=_('name')))
		grid.Add(self._disk_name, 1, wx.EXPAND)

		grid.Add(wx.StaticText(panel, -1, _('Disk description:')))
		self._disk_descr = wx.TextCtrl(panel, -1,
				validator=MyValidator(data_key=(data, 'descr')),
						style=wx.TE_MULTILINE)
		grid.Add(self._disk_descr, 1, wx.EXPAND)

		last_dirs, last_dir = self.__get_last_dirs()

		grid.Add(wx.StaticText(panel, -1, _('Folder:')))
		self._path = wx.ComboBox(panel, -1, last_dir,
				validator=MyValidator(data_key=(data, 'path'),
						validators=validators.NotEmptyValidator(),
						field=_('path')),
				choices=last_dirs)

		size = self._path.GetSizeTuple()[1]
		btn_sel_dir = wx.Button(panel, -1, '...', size=(size, size))

		grid2 = wx.BoxSizer(wx.HORIZONTAL)
		grid2.Add(self._path, 1, wx.EXPAND)
		grid2.Add((5, 1))
		grid2.Add(btn_sel_dir)
		grid.Add(grid2, 1, wx.EXPAND)

		main_grid.Add(grid, 1, wx.EXPAND | wx.ALL, 12)

		panel.SetSizerAndFit(main_grid)

		self.Bind(wx.EVT_BUTTON, self._on_btn_sel_dir, btn_sel_dir)

		return panel

	def _create_page_options(self, parent):
		data = self._data
		if 'load_captions_txt' not in data:
			data['load_captions_txt'] = True

		panel = wx.Panel(parent, -1)
		panel_grid = wx.BoxSizer(wx.VERTICAL)

		main_grid = wx.BoxSizer(wx.VERTICAL)

		main_grid.Add(wx.CheckBox(panel, -1, _('Include empty directories'),
				validator=MyValidator(data_key=(data, 'include_empty'))))

		main_grid.Add((5, 5))

		main_grid.Add(wx.CheckBox(panel, -1, _('Force load files'),
				validator=MyValidator(data_key=(data, 'force'))))

		main_grid.Add((5, 5))

		main_grid.Add(wx.CheckBox(panel, -1, _('Load info from captions.txt'),
				validator=MyValidator(data_key=(data, 'load_captions_txt'))))

		main_grid.Add((5, 12))
		main_grid.Add(_create_label(panel, _('Skipped directories')))
		main_grid.Add((5, 5))

		grid = wx.FlexGridSizer(2, 2, 5, 12)
		grid.AddGrowableCol(1)
		grid.Add(wx.StaticText(panel, -1, _("Don't load:")))
		grid.Add(wx.TextCtrl(panel, -1, validator=MyValidator(
				data_key=(data, 'skip_subdirs'))), 0, wx.EXPAND)
		grid.Add((1, 1))
		grid.Add(_create_small_label(panel, _('(Separate dirs by ";")')))

		main_grid.Add(grid, 1, wx.EXPAND | wx.LEFT, 12)

		panel_grid.Add(main_grid, 1, wx.EXPAND | wx.ALL, 12)
		panel.SetSizerAndFit(panel_grid)
		return panel

	#########################################################################

	def _on_btn_sel_dir(self, evt):
		curr_dir = self._path.GetValue()
		if (curr_dir is None or len(curr_dir) == 0 or not os.path.exists(curr_dir)
				or not os.path.isdir(curr_dir)):
			curr_dir = os.path.abspath(os.curdir)

		dialog = wx.DirDialog(self, _('Select directory'), defaultPath=curr_dir,
				style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)

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

		if self._collection_disk_names is not None and name in self._collection_disk_names:
			message_box_error(self, _('Name already exists in collection!'),
					_('Add disk'))
			return

		current_path = self._data['path']

		if not os.path.exists(current_path):
			message_box_error(self, _("Selected dir don't exists!"), _('Add disk'))
			return

		last_dirs = [current_path] + [path
				for path in (self._path.GetString(idx)
					for idx in xrange(min(self._path.GetCount(), 9)))
				if path != current_path]

		if __name__ != '__main__':
			AppConfig().set_items('add_disk-last_dir', 'last_dir', last_dirs)

		self._data['skip_dirs_list'] = [dirname.strip() \
				for dirname in self._data['skip_subdirs'].split(';')]
		self.EndModal(wx.ID_OK)

	#########################################################################

	def __get_last_dirs(self):
		last_dir = ''
		if __name__ == '__main__':
			last_dirs = []

		else:
			last_dirs = AppConfig().get_items('add_disk-last_dir') or []
			if len(last_dirs) > 0:
				last_dirs = [val for _key, val in sorted(last_dirs)]
				last_dir = last_dirs[0]

		return (last_dirs, last_dir)

	def __load_disk_names(self, collection, update):
		self._collection_disk_names = None
		if collection is not None:
			if update:
				name = self._data['name']
				self._collection_disk_names = tuple((disk.name
						for disk in collection.disks if disk.name != name))

			else:
				self._collection_disk_names = tuple((disk.name
						for disk in collection.disks))


if __name__ == '__main__':

	def _test():
		app = wx.PySimpleApp()
		data = {'name': '__name__', 'descr': '__descr__'}
		wnd = DlgAddDisk(None, data)
		if wnd.ShowModal() == wx.ID_OK:
			print 'OK', data
		else:
			print 'cancel'
		wnd.Destroy()

		del app

	_test()



# vim: encoding=utf8: ff=unix:
