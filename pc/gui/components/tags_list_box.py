# -*- coding: utf-8 -*-

"""
 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004-2007

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


if __name__ == '__main__':
	import sys
	reload(sys)
	try:
		sys.setappdefaultencoding("utf-8")
	except:
		sys.setdefaultencoding("utf-8")


import wx

_ = wx.GetTranslation



class TagsListBox(wx.CheckListBox):
	def __init__(self, *args, **kwargs):
		wx.CheckListBox.__init__(self, *args, **kwargs)

		self._all_tags = []
		self._item_tags = []

	#########################################################################


	@property
	def selected(self):
		return [ tag for idx, tag in enumerate(self._all_tags) 
				if self.IsChecked(idx) ]

	#########################################################################


	def show(self, all_tags, item_tags):
		self._all_tags = all_tags or []
		self._item_tags = item_tags or []
		self._show()

	def _show(self):
		self.Clear()
		for tag in self._all_tags:
			idx = self.Append(tag)
			if tag in self._item_tags:
				self.Check(idx)


	#########################################################################


if __name__ == '__main__':
	app = wx.PySimpleApp()

	class TestDialog(wx.Dialog):
		def __init__(self, *argv, **kwarg):
			wx.Dialog.__init__(self, *argv, **kwarg)
			sizer = wx.BoxSizer(wx.VERTICAL)

			self.tlp = tlp = TagsListBox(self, -1)
			sizer.Add(tlp, 1, wx.EXPAND)

			all_tags = ['a', 'b', 'c', 'd']
			item_tags = ['b', 'd']
			tlp.show(all_tags, item_tags)

			sizer.Add(self.CreateStdDialogButtonSizer(wx.OK|wx.CANCEL), 0, 
					wx.EXPAND|wx.ALL, 5)

			self.SetSizer(sizer)
			sizer.Fit(self)

	wnd = TestDialog(None)
	if wnd.ShowModal() == wx.ID_OK:
		print 'OK', wnd.tlp.selected
	else:
		print 'cancel'
	wnd.Destroy()

	del app



# vim: encoding=utf8: ff=unix:
