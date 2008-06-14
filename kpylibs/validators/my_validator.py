# -*- coding: utf-8 -*-
'''
$Id$
'''

__revision__ = '0.1'
__all__ = ['MyValidator']


import types

import gettext
_ = gettext.gettext


import wx



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
		"""
		"""
		return MyValidator(self._data, self._validators, self._field)


	def Validate(self, win):
		"""
			Validacja pola
		"""
		text_ctrl = self.GetWindow()
		value = text_ctrl.GetValue()

		if self._validators is not None:
			for validator in self._validators:
				if not validator.validate(value):
					dlg = wx.MessageDialog(win,
							_('Validate field "%(field)s" failed:\n%(msg)s') %
									dict(field=(self._field or ''), msg=validator.get_error()), 
							_('Validate error'), 
							wx.OK|wx.CENTRE|wx.ICON_ERROR)
					dlg.ShowModal()
					dlg.Destroy()
					text_ctrl.SetBackgroundColour('red')

					text_ctrl.SetFocus()
					text_ctrl.Refresh()
					return False
		
		text_ctrl.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
		text_ctrl.Refresh()
		return True


	def TransferToWindow(self):
		if self._data is not None:
			text_ctrl = self.GetWindow()
			data, key = self._data
			val = data.get(key, "") or ''
			if isinstance(text_ctrl, wx.CheckBox) or isinstance(text_ctrl, wx.RadioButton):
				text_ctrl.SetValue(bool(val))
			else:
				text_ctrl.SetValue(str(val))
		return True 


	def TransferFromWindow(self):
		if self._data is not None:
			text_ctrl = self.GetWindow()
			data, key = self._data
			value = text_ctrl.GetValue()
			if self._validators is not None:
				for validator in self._validators:
					value = validator.convert_value_from_window(value)
			data[key] = value
		return True


# vim: encoding=utf8: ff=unix:
