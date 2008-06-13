#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from kpylibs.validators import MyValidator

from _base_field import BaseField



class ComboField(BaseField):
	def __init__(self, parent, label, key, fieldname=None, readonly=False, expand=False,
			min_length=0, max_length=-1, regexpr=None, style=0, items=None):
		BaseField.__init__(self, parent, label, key, readonly=False, expand=False)
		self._style = style
		self._items = items
		self._min_length = min_length
		self._max_length = max_length
		self._regexpr	= regexpr


	@property
	def control(self):
		if self._control is None:
			# walidatory
			validators = self._get_validators()
			# kontrolka
			self._control = wx.ComboBox(self._parent, -1, style=self._style,
					validator=MyValidator(data_key=(self._parent.data, self._key),
						validators=validators, field=self._fieldname
					)
			)
			if self._parent.data.has_key(self._key + ":items"):
				self._items = self._parent.data[self._key + ":items"]
			self._load_items()
			if self._readonly:
				self._control.Disable()
		return self._control


	def set_items(self, items):
		self._items = items
		self._load_items()
		
	
	@property
	def value(self):
		if self._control is None:
			return None
		return self._control.GetValue()


	def select(self, value):
		control = self.control
		control.SetValue(value)


	def _load_items(self):
		control = self.control
		[ control.Append(key, val) for (key, val) in self._items ]


	def _get_validators(self):
		validators = []
		if self._min_length > 0:
			validators.append(MinLenValidator(self._min_length))
		if self._max_length > 0:
			validators.append(MaxLenValidator(self._max_length))
		if self._regexpr is not None:
			validators.append(ReValidator(self._regexpr))
		return validators


# vim: encoding=utf8:
