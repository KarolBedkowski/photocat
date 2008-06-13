#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

if __name__ == '__main__':
	import sys
	sys.path.append('../..')


import wx

from autodialog 	import AutoDialog
from text_field		import TextField
from combo_field	import ComboField
from combo_value_field	import ComboValueField
from label_field	import LabelField
from date_field		import DateField
from checkbox_field	import CheckBoxField
from radiobuttons_field	import RadioButtonsField
from button			import Button



class TstAutoDlg(AutoDialog):
	
	dialog_caption = 'test'
	dialog_size		= (300, 300)

	def _fields(self):
		return [
				TextField(self, 'val1', 'val1'),
				TextField(self, 'val2', 'val2', 'Val2', expand=True, multiline=True),
				TextField(self, 'val3', 'val3', '', min_length=3, max_length=5),
				TextField(self, 'val4', 'val4', '', regexpr=r'^\d+$'),
				LabelField(self, 'label'),
				ComboField(self, 'cb1', 'cb1'),
				ComboValueField(self, 'cb2', 'cb2', items=[('a', 1), ('b', 2)]),
				DateField(self, 'data', 'data', notempty=True),
				CheckBoxField(self, 'checkbox', 'valcheckbox'),
				RadioButtonsField(self, 'Radio', 'rdbtn1'),
				Button(self, 'My Button', self._on_bttn)
		]


	def _on_bttn(self, evt):
		print '_on_bttn'



app = wx.PySimpleApp()
data = {
		'val1': '123',
		'val2': 'abncd',
		'cb1': 'akaka',
		'cb1:items':  [('a', 1), ('b', 2)],
		'cb2': 12,
		'valcheckbox': False,
		'rdbtn1': 2,
		'rdbtn1:items': [('akaal', 1), ('o2owo', 2) ],
}
dlg = TstAutoDlg(None, data)
dlg.ShowModal()

print data


# vim: encoding=utf8:
