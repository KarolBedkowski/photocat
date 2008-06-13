#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from kpylibs.validators import MyValidator, IntValidator, FloatValidator

from _base_field import BaseField



class NumberField(BaseField):
	def __init__(self, parent, label, key, fieldname=None, readonly=False, only_int=False):
		BaseField.__init__(self, parent, label, key, fieldname, readonly, False)
		self._only_int = only_int


	@property
	def control(self):
		if self._control is None:
			# walidatory
			validators = self._get_validators()
			# kontrolka
			self._control = wx.TextCtrl(self._parent, -1,
					validator=MyValidator(
						data_key=(self._parent.data, self._key), 
						validators=validators, 
						field=self._fieldname
					)
			)
			# reszta opcji
			self._control.SetEditable(not self._readonly)
		return self._control


	@property
	def value(self):
		return self.control.GetValue()


	def _get_validators(self):
		validators = []
		if self._only_int:
			validators.append(IntValidator())
		else:
			validators.append(FloatValidator())
		return validators


# vim: encoding=utf8:
