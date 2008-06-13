#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from kpylibs.validators import MyValidator

from _base_field import BaseField



class CheckBoxField(BaseField):
	

	def __init__(self, parent, label, key, fieldname=None, readonly=False, group_label=None, style=0):
		BaseField.__init__(self, parent, group_label or '', key, fieldname, readonly, False)
		self._style		= style
		self._checkbox_label = label


	@property
	def control(self):
		if self._control is None:
			self._control = wx.CheckBox(self._parent, -1, self._checkbox_label,
					style=self._style,
					validator=MyValidator(
						data_key=(self._parent.data, self._key), 
						field=self._fieldname
					)
			)
		return self._control


	@property
	def value(self):
		return self.control.GetValue()


# vim: encoding=utf8:
