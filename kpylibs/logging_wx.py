#!/usr/bin/python2.4
# -*- coding: utf8 -*-
"""
Logging setup.

"""
__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id: logging_setup.py 5 2007-06-05 20:27:47Z k $'

__all__ = ['logging_setup']


import logging

import wx



class MyLog(wx.PyLog):
	
	def __init__(self, header='wx'):
		wx.PyLog.__init__(self)
		self._logger = logging.getLogger(header)

	def DoLogString(self, message, dummy):
		if message.startswith("Debug"):
			self._logger.debug(message)
		else:
			self._logger.info(message)
		



def logging_setup_wx(header='wx'):
	wx.Log_SetActiveTarget(MyLog(header))


# vim: ff=unix: encoding=utf8: 
