# -*- coding: utf-8 -*-
'''
$Id$
'''

__revision__ = '0.1'
__all__ = ['MyValidator']


import types

import wx

from my_validator import MyValidator

class MyValidatorDv(MyValidator):
	def __init__(self, data_key=None, validators=None, field=None):
		"""
			@param data_key = tuple(dict(), key)
			@param validators = [ SimpleValidator() ]
			@param field = field name
		"""
		MyValidator.__init__(self, data_key, validators, field)


	def Clone(self):
		"""
		"""
		return MyValidatorDv(self._data, self._validators, self._field)


	def TransferToWindow(self):
		if self._data is not None:
			text_ctrl = self.GetWindow()
			data, key = self._data
			val = data.get(key, None) or None
			
			for i in xrange(text_ctrl.GetCount()):
				if text_ctrl.GetClientData(i) == val:
					text_ctrl.Select(i)
					break
		return True 


	def TransferFromWindow(self):
		if self._data is not None:
			text_ctrl = self.GetWindow()
			data, key = self._data
			try:
				data[key] = text_ctrl.GetClientData(text_ctrl.GetSelection())
			except:
				data[key] = None
		return True


# vim: encoding=utf8: ff=unix:
