#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from _base_field import BaseField



class _MyRBValidator(wx.PyValidator):
	def __init__(self, data_key=None, value=None):
		"""
			@param data_key = tuple(dict(), key)
			@param field = field name
		"""
		wx.PyValidator.__init__(self)
		self._data = data_key
		self._value = value


	def Clone(self):
		"""
		"""
		return _MyRBValidator(self._data, self._value)


	def Validate(self, win):
		"""
			Validacja pola
		"""
		return True


	def TransferToWindow(self):
		if self._data is not None:
			data, key = self._data
			val = data.get(key, "") or ''
			self.GetWindow().SetValue(val == self._value)
		return True 


	def TransferFromWindow(self):
		if self._data is not None:
			if self.GetWindow().GetValue():
				data, key = self._data
				data[key] = self._value
		return True



class RadioButtonsField(BaseField):
	def __init__(self, parent, label, key, fieldname=None, readonly=False):
		BaseField.__init__(self, parent, label, key, fieldname, readonly, False)
		self._grid		= None

	@property
	def control(self):
		if self._grid is None:
			items = self._items = self._parent.data[self._key + ":items"]
			if len(items) > 0:
				self._control = [ wx.RadioButton(self._parent, -1, items[0][0], style=wx.RB_GROUP,
						validator=_MyRBValidator((self._parent.data, self._key), items[0][1])
				)]
				self._control += [ wx.RadioButton(self._parent, -1, item[0],
						validator=_MyRBValidator((self._parent.data, self._key), item[1])
				) for item in items[1:] ]

			self._grid = grid = wx.BoxSizer(wx.VERTICAL)
			[ grid.Add(control, 0, wx.EXPAND) for control in self._control ]

		return self._grid


	@property
	def value(self):
		for idx in xrange(len(self._items)):
			if self._control[idx].GetValue():
				return self._items[idx][1]
		return None


# vim: encoding=utf8:
