#!/usr/bin/python2.4
# -*- coding: utf8 -*-
# pylint: disable-msg=W0401, C0103
"""
dialog_list

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
__copyright__	= 'Copyright (C) Karol Będkowski 2007'
__revision__ = '$Id$'

__all__ = ['DialogList', 'PanelList']



import wx

(BUTTON_ADD, BUTTON_DEL, BUTTON_UP, BUTTON_DOWN) = (1, 2, 4, 8)

class PanelList(wx.Panel):
	def __init__(self, parent, buttons=3):
		wx.Panel.__init__(self, parent, -1)
		
		self._listbox	= wx.ListBox(self, -1, size=(200, 200), style=wx.LB_SINGLE)
		self._btns		= {}

		grid_buttons = wx.BoxSizer(wx.VERTICAL)
		def add_btn(label, name):
			btn	= wx.Button(self, -1, label, size=(30, -1))
			grid_buttons.Add(btn, 0, wx.EXPAND)
			grid_buttons.Add((3, 3))
			self._btns[name] = btn

		if buttons & BUTTON_ADD:	add_btn('+', 'add')
		if buttons & BUTTON_DEL:	add_btn('-', 'del')
		if buttons & BUTTON_UP:		add_btn('^', 'up')
		if buttons & BUTTON_DOWN:	add_btn('v', 'down')

		main_grid = wx.BoxSizer(wx.HORIZONTAL)
		main_grid.Add(self._listbox, 1, wx.EXPAND)
		main_grid.Add((3, 3))
		main_grid.Add(grid_buttons)

		self.SetSizerAndFit(main_grid)

	@property
	def listbox(self):
		return self._listbox

	@property
	def selected(self):
		try:
			return self._listbox.GetClientData(self._listbox.GetSelection())
		except:
			return None

	def get_button(self, name):
		return self._btns[name]

	def bind_button(self, name, wnd, function):
		wnd.Bind(wx.EVT_BUTTON, function, self._btns[name])

	def bind_listbox_dclick(self, wnd, function):
		wnd.Bind(wx.EVT_LISTBOX_DCLICK, function, self._listbox)

	def fill(self, items):
		listctrl = self._listbox
		listctrl.Clear()
		[ listctrl.Append(item[0], item[1]) for item in items ]



class DialogList(wx.Dialog):
	def __init__(self, parent, caption=''):
		wx.Dialog.__init__(self, parent, -1, caption, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

		self._panel_list = panel = PanelList(self)

		self._listbox		= panel.listbox

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.Centre(wx.BOTH)

		panel.fill(self._get_list_items())

		panel.bind_listbox_dclick(self, self._on_listbox)
		panel.bind_button('add', self, self._on_button_add)
		panel.bind_button('del', self, self._on_button_del)


	def refresh(self):
		self._panel_list.fill(self._get_list_items())


	@property
	def selected(self):
		try:
			return self._listbox.GetClientData(self._listbox.GetSelection())
		except:
			return None

	def _get_list_items(self):
		return []


	def _on_button_add(self, evt):
		print '_on_button_add'


	def _on_button_del(self, evt):
		print '_on_button_del'

	def _on_listbox(self, evt):
		pass


if __name__ == '__main__':
	app = wx.PySimpleApp()
	dialog = DialogList(None)
	result = dialog.ShowModal()
	dialog.Destroy()



# vim: encoding=utf8:
