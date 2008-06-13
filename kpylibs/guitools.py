#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=W0142
"""
Funkcje pomocnicze 

 kPyLibs
 Copyright (c) Karol Będkowski, 2007

 This file is part of kPyLibs

 SAG is free software; you can redistribute it and/or modify it under the
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

__all__			= []


import types

import wx


def create_toolbar_button(parent, caption, function, image=None, imgid=None, description=''):
	""" create_toolbar_button(parent, caption, function, [image], [imgid], [description]) -> button id
		-- utworzenie przycisku na toolbarze 
	"""
	if imgid is not None:
		image = wx.ArtProvider_GetBitmap(imgid, wx.ART_TOOLBAR, (16, 16))
	if type(caption) == types.IntType:
		caption = wx.GetStockLabel(caption, False)

	btn_id = wx.NewId()
	parent.AddSimpleTool(btn_id, image, caption, description)
	wx.EVT_TOOL(parent, btn_id, function)
	return btn_id


def create_toolbar_togglebutton(parent, caption, function, image):
	""" create_toolbar_togglebutton(parent, caption, function, image) -> button id
		-- utworzenie przycisku na toolbarze 
	"""
	btn_id = wx.NewId()
	parent.AddCheckTool(btn_id, image, shortHelp=caption)
	wx.EVT_TOOL(parent, btn_id, function)
	return btn_id


def create_menu_item(wnd, menu, label, description, function, pos=None):
	''' create_menu_item(wnd, menu, label, description, function, [pos]) -> None
		-- utworzenie elementu menu 
	'''
	mid = wx.NewId()
	if pos is None:
		menu.Append(mid, label, description)
	else:
		menu.Insert(pos, mid, label, description)
	wx.EVT_MENU(wnd, mid, function)


def create_button(wnd, label, function, wxid=-1, *args, **kward):
	''' create_button(wnd, label, funtion, *args, **kward) -> wxButton --  utworznie buttona'''
	button = wx.Button(wnd, wxid, label or wx.EmptyString, *args, **kward)
	wnd.Bind(wx.EVT_BUTTON, function, button)
	return button


def create_menu(wnd, items):
	menu = wx.Menu()

	def add(label, accel, description, function, wxid=None, img=None):
		if label is None:
			if wxid is None:
				label = wx.EmptyString
			else:
				if wx.VERSION[1] > 6:
					label = wx.GetStockLabel(wxid)
				else:
					label = wx.GetStockLabel(wxid, True, accel or '')
		elif type(label) == types.IntType:
			if wx.VERSION[1] > 6:
				label = wx.GetStockLabel(label)
			else:
				label = wx.GetStockLabel(label, True, accel or '')
		elif accel is not None:
			label = '%s\t%s' % (label, accel)

		if wxid is None or wxid == -1:
			wxid = wx.NewId()

		menu_item = wx.MenuItem(menu, wxid, label, description or '')

		if img is not None:
			menu_item.SetBitmap(img)

		menu.AppendItem(menu_item)
		return wxid

	for item in items:
		if len(item) == 1 and item == '-':
			menu.AppendSeparator()
		else:
			if len(item) == 6:
				label, accel, description, function, wxid, img = item
				if type(img) == types.UnicodeType:
					img = wx.ArtProvider_GetBitmap(img, wx.ART_MENU, (16, 16))
				wxid = add(label, accel, description, function, wxid, img)
			elif len(item) == 5:
				label, accel, description, function, wxid = item
				wxid = add(label, accel, description, function, wxid)
			else:
				label, accel, description, function = item
				wxid = add(label, accel, description, function)

			wnd.Bind(wx.EVT_MENU, function, id=wxid)

	return menu



def combobox_select_item(control, data):
	for i in xrange(control.GetCount()):
		if control.GetClientData(i) == data:
			control.Select(i)
			break

def combobox_get_selected_item(control):
	try:
		return control.GetClientData(control.GetSelection())
	except:
		return None


# vim: encoding=utf8: ff=unix: 
