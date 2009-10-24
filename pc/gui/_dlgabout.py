#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004-2008

 This file is part of Photo Catalog

 PC is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 PC is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006-2008'
__revision__	= '$Id$'

__all__			= ['show_about_box']


import sys

import wx
from wx.lib.wordwrap import wordwrap

_ = wx.GetTranslation



def show_about_box(parent):
	import pc
	params = {
		'version': pc.__version__,
		'wxversion': wx.VERSION_STRING,
		'pyversion': sys.version,
	}

	info = wx.AboutDialogInfo()
	info.Name = "PhotoCatalog"
	info.Version = pc.__version__
	info.Copyright = "(C) Karol Będkowski 2007,2008"
	#info.Description = wordwrap('''''', 350, wx.ClientDC(parent))
	#info.WebSite = ("http://en.wikipedia.org/wiki/Hello_world", "Hello World home page")
	info.Developers = [ "Karol Będkowski" ]	
	info.License = wordwrap('''
PC is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 2.

PC is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.


Python %(pyversion)s
Copyright (c) 2001-2007 Python Software Foundation.

wxPython %(wxversion)s
Copyright (c) 1998 Julian Smart, Robert Roebling et al

EXIF.py (15-02-2004)
Copyright 2002 Gene Cash All rights reserved.
''' % params, 500, wx.ClientDC(parent))
	wx.AboutBox(info)
	




# vim: encoding=utf8:
