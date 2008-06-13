#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx



class AutoDialog(wx.Dialog):

	dialog_caption	= None
	dialog_size		= wx.DefaultSize

	def __init__(self, parent, data, caption=None):

		assert data is not None

		if caption is None:
			caption = self.dialog_caption 

		wx.Dialog.__init__(self, parent, -1, caption or '', style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

		self._data = data

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_fields_grid(), 1, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.SetSize(self.dialog_size)
		self.Centre(wx.BOTH)
		
		wx.EVT_BUTTON(self, wx.ID_OK, self._on_ok)


	def _create_fields_grid(self):
		fields_grid = wx.FlexGridSizer(5, 2, 4, 4)
		fields_grid.AddGrowableCol(1)

		data = self._data
		
		x = 0
		for field in self._fields():
			fields_grid.Add(field.label, 0, wx.EXPAND)
			fields_grid.Add(field.control, 1, wx.EXPAND)
			if field.expand:
				fields_grid.AddGrowableRow(x)
			x += 1

		return fields_grid


	def _fields(self):
		return []


	def _on_ok(self, evt):
		if not self.Validate():
			return

		if not self.TransferDataFromWindow():
			return

		if not self._validate():
			return

		self.EndModal(wx.ID_OK)


	@property
	def data(self):
		return self._data


	def _validate(self):
		return True

# vim: encoding=utf8:
