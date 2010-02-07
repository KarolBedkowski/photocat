# -*- coding: utf-8 -*-
'''
validators/my_validator.py

 kpylibs 1.x
 Copyright (c) Karol Będkowski, 2006-2008

 This file is part of kpylibs

 kpylibs is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.
'''

__all__ = ['MyValidator']


import types

import wx
import wx.calendar
import wx.lib.masked

from validators.errors	import ValidateError

_ = wx.GetTranslation



##############################################################################



class MyValidator(wx.PyValidator):
	def __init__(self, data_key=None, validators=None, field=None):
		"""
			@param data_key = tuple(dict(), key)
			@param validators = [ SimpleValidator() ]
			@param field = field name
		"""
		wx.PyValidator.__init__(self)
		self._data = data_key
		if type(validators) == types.ListType or type(validators) == types.TupleType or validators is None:
			self._validators = validators

		else:
			self._validators = [validators]

		self._field = field


	def Clone(self):
		"""	"""
		return MyValidator(self._data, self._validators, self._field)


	def Validate(self, win):
		""" Validacja pola """
		control = self.GetWindow()

		if isinstance(control, wx.calendar.CalendarCtrl):
			value = control.GetDate()

		else:
			value = control.GetValue()

		if self._validators is not None:
			for validator in self._validators:
				try:
					value = validator.value_from_window(value)

				except ValidateError, err:
					dlg = wx.MessageDialog(win,
							_('Validate field "%(field)s" failed:\n%(msg)s') %
									dict(field=(self._field or self._data[1] or ''), msg=validator.error),
							_('Validate error'),
							wx.OK|wx.CENTRE|wx.ICON_ERROR)
					dlg.ShowModal()
					dlg.Destroy()
					control.SetBackgroundColour('red')

					control.SetFocus()
					control.Refresh()
					return False

		control.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		control.Refresh()
		return True


	def TransferToWindow(self):
		if self._data:
			control = self.GetWindow()
			data, key = self._data
			if hasattr(data, key):
				val = getattr(data, key)

			else:
				val = data.get(key)

			if self._validators is not None:
				validators = self._validators[:]
				validators.reverse()
				for validator in validators:
					val = validator.value_to_window(val)

			if isinstance(control, wx.lib.masked.NumCtrl):
				control.SetValue(val or 0)

			elif isinstance(control, wx.CheckBox) or isinstance(control, wx.RadioButton):
				control.SetValue(bool(val))

			elif isinstance(control, wx.calendar.CalendarCtrl):
				control.SetDate(val or '')

			else:
				control.SetValue(str(val or ''))

		return True


	def TransferFromWindow(self):
		if self._data is not None:
			control = self.GetWindow()
			data, key = self._data

			if isinstance(control, wx.calendar.CalendarCtrl):
				value = control.GetDate()

			else:
				value = control.GetValue()

			if self._validators is not None:
				for validator in self._validators:
					value = validator.value_from_window(value)

			if hasattr(data, key):
				setattr(data, key, value)

			else:
				data[key] = value

		return True


# vim: encoding=utf8: ff=unix:
