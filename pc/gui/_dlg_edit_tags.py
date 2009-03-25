#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
 Photo Catalog v 1.x  (pc)
 Copyright (c) Karol Będkowski, 2004-2009

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
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'

__all__			= ['DlgEditTags', 'show_dlg_edit_tags']


if __name__ == '__main__':
	import sys
	reload(sys)
	try:
		sys.setappdefaultencoding("utf-8")
	except:
		sys.setdefaultencoding("utf-8")
	sys.path.append('../../')


import sys
import os
import time

import wx
import wx.gizmos   as  gizmos

if __name__ == '__main__':
	app = wx.PySimpleApp()

_ = wx.GetTranslation


_LABEL_FONT_STYLE = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
_LABEL_FONT_STYLE.SetWeight(wx.FONTWEIGHT_BOLD)

def _creata_label(parent, title):
	ctr = wx.StaticText(parent, -1, title)
	ctr.SetFont(_LABEL_FONT_STYLE)
	return ctr



class DlgEditTags(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, -1, _('Properties'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)

		dlg_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid = wx.BoxSizer(wx.VERTICAL)

		main_grid.Add(_creata_label(self, _("Tags")))

		self._elb_tags = gizmos.EditableListBox(self, -1, '')
		main_grid.Add(self._elb_tags, 1, wx.EXPAND|wx.LEFT|wx.TOP, 12)

		dlg_grid.Add(main_grid, 1, wx.EXPAND|wx.ALL, 12)

		dlg_grid.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 12)

		self.SetSizerAndFit(dlg_grid)
		self.SetSize((300, 400))
		self.Center()

		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)


	def _get_tags(self):
		return self._elb_tags.GetStrings()

	def _set_tags(self, tags):
		self._elb_tags.SetStrings(tags)

	tags = property(_get_tags, _set_tags)


	##################################################################


	def _on_ok(self, evt):
		self.EndModal(wx.ID_OK)



def show_dlg_edit_tags(parent, tag_provider):
	wnd = DlgEditTags(parent)
	wnd.tags = tag_provider.tags

	updated = False

	if wnd.ShowModal() == wx.ID_OK:
		updated = sorted(tag_provider.tags or []) != sorted(wnd.tags or [])
		if updated:
			tag_provider.tags = wnd.tags

	wnd.Destroy()
	return updated





if __name__ == '__main__':
	wnd = DlgEditTags(None)
	wnd.tags = ['test', 'ok', 'tu']
	if wnd.ShowModal() == wx.ID_OK:
		print 'OK', wnd.tags
	else:
		print 'cancel'
	wnd.Destroy()

	del app




# vim: encoding=utf8:
