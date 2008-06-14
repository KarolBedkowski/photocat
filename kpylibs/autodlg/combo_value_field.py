#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from kpylibs.validators import MyValidatorDv

from combo_field import ComboField



class ComboValueField(ComboField):
	def __init__(self, parent, label, key, fieldname=None, readonly=False, expand=False, style=wx.CB_READONLY, 
			items=None):
		ComboField.__init__(self, parent, label, key, fieldname, readonly, expand, style=style, items=items)


	@property
	def control(self):
		if self._control is None:
			self._control = wx.ComboBox(self._parent, -1, style=self._style,
					validator=MyValidatorDv(data_key=(self._parent.data, self._key),
						field=self._fieldname
					)
			)
			if self._parent.data.has_key(self._key + ":items"):
				self._items = self._parent.data[self._key + ":items"]
			self._load_items()
			if self._readonly:
				self._control.Disable()
		return self._control


	@property
	def value(self):
		if self._control is None:
			return None
		try:
			return self._control.GetClientData(self._control.GetSelection())
		except:
			return None


	def select(self, value):
		control = self.control
		for i in xrange(control.GetCount()):
			if control.GetClientData(i) == value:
				control.Select(i)
				break


# vim: encoding=utf8:
