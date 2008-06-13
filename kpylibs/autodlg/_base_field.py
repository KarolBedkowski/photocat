#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""

"""
__revision__ = '$Id$'

import wx

class BaseField(object):
	def __init__(self, parent, label, key, fieldname=None, readonly=False, expand=False):
		self._parent = parent
		self._label = label
		self._key = key
		self._readonly = readonly
		self._expand = expand
		self._fieldname = fieldname or label
		self._control = None


	@property
	def label(self):
		if self._label:
			return wx.StaticText(self._parent, -1, self._label)
		return (0, 0)


	@property
	def control(self):
		return None


	@property
	def expand(self):
		return self._expand


	@property
	def value(self):
		return None

# vim: encoding=utf8:
