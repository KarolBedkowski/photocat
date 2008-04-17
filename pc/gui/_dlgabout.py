#!/usr/bin/python2.4
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

__all__			= ['DlgAbout']

import sys

import wx
import wx.html

_ = wx.GetTranslation

_ABOUT_TEXT = '''
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	</head>
	<body>
		<h1>PC</h1>
		<p>ver. %(version)s</p>
		<p><i>Copyright &copy; Karol Będkowski 2007,2008</i></p>
		<p>
			PC is free software; you can redistribute it and/or modify it under the
			terms of the GNU General Public License as published by the Free Software
			Foundation, version 2.
		</p>
		<p>
			PC is distributed in the hope that it will be useful, but WITHOUT ANY
			WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
			FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
			details.
		</p>
		<p><b>Biblioteki:</b>
			<dl>
				<dt>Python %(pyversion)s</dt>
				<dd>Copyright (c) 2001-2007 Python Software Foundation.</dd>

				<dt>wxPython %(wxversion)s</dt>
				<dd>Copyright (c) 1998 Julian Smart, Robert Roebling et al</dd>

				<dt>EXIF.py (15-02-2004)</dt>
				<dd>Copyright 2002 Gene Cash All rights reserved.</dd>
			</dl>
		</p>
	</html>
</body>

''' 


class DlgAbout(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, _('About'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

		main_grid = wx.BoxSizer(wx.VERTICAL)
		

		self.__html_box = wx.html.HtmlWindow(self, -1)
		self.__html_box.SetFonts("helvetica", "courier", [6,7,8,9,10,11,12])
		main_grid.Add(self.__html_box, 1, wx.EXPAND|wx.ALL, 5)
		
		main_grid.Add(self.CreateStdDialogButtonSizer(wx.OK), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.SetSize((500, 300))
		self.Centre(wx.BOTH)

		self.Bind(wx.EVT_KEY_DOWN, self.__on_key_pressed)

		import pc

		params = {
			'version': pc.__version__,
			'wxversion': wx.VERSION_STRING,
			'pyversion': sys.version,
		}

		self.__html_box.SetPage(_ABOUT_TEXT % params)


	def __on_key_pressed(self, evt):
		""" Zamknięcie okna po naciśnięciu esc """
		key = evt.KeyCode()
		if key == 27 or key == 13:
			self.EndModal(wx.ID_OK)
		else:
			evt.Skip()


# vim: encoding=utf8:
