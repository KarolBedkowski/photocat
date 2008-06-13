#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from kpylibs.dialogs	import dialog_get_date
from kpylibs.validators import MyValidator, DateValidator, NotEmptyValidator

from _base_field import BaseField



class DateField(BaseField):
	

	def __init__(self, parent, label, key, fieldname=None, readonly=False, notempty=False):
		BaseField.__init__(self, parent, label, key, fieldname, readonly, False)
		self._button	= None
		self._grid		= None
		self._notempty	= notempty


	@property
	def control(self):
		if self._grid is None:
			validators = []
			if self._notempty:
				validators.append(NotEmptyValidator())
			validators.append(DateValidator())
			# kontrolka
			self._control = wx.TextCtrl(self._parent, -1,
					validator=MyValidator(
						data_key=(self._parent.data, self._key), 
						validators=validators, 
						field=self._fieldname
					)
			)
			size = self._control.GetSizeTuple()[1]
			self._button = wx.Button(self._parent, -1, '...', size=(size, size))

			self._parent.Bind(wx.EVT_BUTTON, self._on_btn_select_date, self._button)

			self._grid = grid = wx.BoxSizer(wx.HORIZONTAL)
			grid.Add(self._control, 1, wx.EXPAND)
			grid.Add((4,4))
			grid.Add(self._button, 0, wx.EXPAND)

			# reszta opcji
			self._control.SetEditable(not self._readonly)
		return self._grid


	@property
	def value(self):
		return self._control.GetValue()


	def _on_btn_select_date(self, evt):
		value = dialog_get_date(self._parent, self.value)
		if value is not None:
			self._control.SetValue(value)



# vim: encoding=utf8:
