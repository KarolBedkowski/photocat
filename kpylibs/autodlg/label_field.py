#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

from _base_field import BaseField


class LabelField(BaseField):
	def __init__(self, parent, label1, label2=None):
		BaseField.__init__(self, parent, label1, None)
		self._label2 = label2


	@property
	def control(self):
		if self._control is None:
			if self._label2 is None:
				self._control = (0, 0)
			else:
				self._control = wx.StaticText(self._parent, -1, label2)
		return self._control



# vim: encoding=utf8:
