#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Shell

 KPyLibs
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

 This file is part of KPyLibs

 KPyLibs is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 SAG is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'

__all__			= ['WndShell']


import logging
_LOG = logging.getLogger(__name__)


import wx
import wx.py



class WndShell(wx.Frame):
	''' Okno shella '''

	def __init__(self, parent, locals_vars):
		wx.Frame.__init__(self, parent, -1, 'Shell', size=(700, 500))
		wx.py.crust.Crust(self, locals=locals_vars)
		self.Centre(wx.BOTH)
		_LOG.debug('WndShell.__init__()')



# vim: encoding=utf8:
