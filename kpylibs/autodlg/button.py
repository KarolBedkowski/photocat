#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from _base_field import BaseField


class Button(BaseField):
	def __init__(self, parent, label1, function, label2=None):
		BaseField.__init__(self, parent, label2 or '', None)
		self._label1 = label1
		self._function = function


	@property
	def control(self):
		if self._control is None:
			self._control = wx.Button(self._parent, -1, self._label1)
			self._parent.Bind(wx.EVT_BUTTON, self._function, self._control)
		return self._control



# vim: encoding=utf8:
