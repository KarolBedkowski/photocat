#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from kpylibs.validators import MyValidator, ReValidator, NotEmptyValidator, MaxLenValidator, MinLenValidator

from _base_field import BaseField



class TextField(BaseField):
	def __init__(self, parent, label, key, fieldname=None, readonly=False, expand=False, multiline=False,
			min_length=0, max_length=-1, regexpr=None, style=0):
		BaseField.__init__(self, parent, label, key, fieldname, readonly, expand)
		self._min_length = min_length
		self._max_length = max_length
		self._regexpr	= regexpr
		self._multiline	= multiline
		self._style		= style


	@property
	def control(self):
		if self._control is None:
			# style
			style = self._get_styles()
			# walidatory
			validators = self._get_validators()
			# kontrolka
			self._control = wx.TextCtrl(self._parent, -1,
					style=style,
					validator=MyValidator(
						data_key=(self._parent.data, self._key), 
						validators=validators, 
						field=self._fieldname
					)
			)
			# reszta opcji
			self._control.SetEditable(not self._readonly)
			if self._max_length > 0:
				self._control.SetMaxLength(self._max_length)
		return self._control


	@property
	def value(self):
		return self.control.GetValue()


	def _get_styles(self):
		style = self._style
		if self._multiline:
			style = wx.TE_MULTILINE|wx.TE_PROCESS_TAB
		return style


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
