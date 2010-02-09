#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=W0142
"""
Funkcje pomocnicze

kPyLibs
Copyright (c) Karol Będkowski, 2007

This file is part of kPyLibs
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'

__all__ = []


import types

import wx


def create_toolbar_button(parent, caption, function, image=None, imgid=None,
		description=''):
	""" create_toolbar_button(parent, caption, function, [image], [imgid],
	[description]) -> button id
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


def create_button(wnd, label, function, wxid=-1, *args, **kward):
	''' create_button(wnd, label, funtion, *args, **kward) -> wxButton
	-- utworznie buttona'''
	button = wx.Button(wnd, wxid, label or wx.EmptyString, *args, **kward)
	wnd.Bind(wx.EVT_BUTTON, function, button)
	return button


def create_menu_item(wnd, menu, label, function=None, description=None,
		accel=None, wxid=None, img=None, pos=None):
	""" create_menu_item(wnd, menu, label, [function], [description], [accel],
	[wxid], [img], [pos]) -> (wxid, menu_item) -- dodanie elementu menu

	@param wnd		okno
	@param menu 	menu
	@param label	etykieta - jeżeli None to jeżeli wxid != None - pobranie
	z Stock etykiety na podstawie wxid
	@param accel	skrót klawiszowy [opcja]
	@param description opis [opcja]
	@param function	callback do podpięcia [opcja]
	@param wxid		id elementu [opcja] domyslnie - generowany
	@param img		bitmapa elementu [opcja]
	@param pos		pozycja do wstawienia elementu [opcja]
	@return (wxid, menu_item)
	"""
	if label is None:
		if wxid is None:
			label = wx.EmptyString
		elif wx.VERSION[1] > 6:
			label = wx.GetStockLabel(wxid, wx.STOCK_WITH_ACCELERATOR)
		else:
			label = wx.GetStockLabel(wxid, True, accel or '')
	elif type(label) == types.IntType:
		if wx.VERSION[1] > 6:
			label = wx.GetStockLabel(label, wx.STOCK_WITH_ACCELERATOR)
		else:
			label = wx.GetStockLabel(label, True, accel or '')
	elif accel is not None:
		label = '%s\t%s' % (label, accel)

	if wxid is None or wxid == -1:
		wxid = wx.NewId()

	if label.startswith('[x]'):
		label = label[3:]
		menu_item = wx.MenuItem(menu, wxid, label, description or '', wx.ITEM_CHECK)
	elif label.startswith('[o]'):
		label = label[3:]
		menu_item = wx.MenuItem(menu, wxid, label, description or '', wx.ITEM_RADIO)
	else:
		menu_item = wx.MenuItem(menu, wxid, label, description or '')

	if img is not None:
		menu_item.SetBitmap(img)

	if pos is None:
		menu.AppendItem(menu_item)
	else:
		menu.InsertItem(pos, menu_item)

	if function is not None:
		wnd.Bind(wx.EVT_MENU, function, id=wxid)

	return wxid, menu_item


def create_menu(wnd, items):
	''' create_menu(wnd, items) -> wxMenu -- stworzenie menu na podstawie listy'''
	menu = wx.Menu()

	for item in items:
		if len(item) == 1 and item == '-':
			menu.AppendSeparator()
		else:
			if len(item) == 6:
				label, accel, description, function, wxid, img = item
				if type(img) == types.UnicodeType:
					img = wx.ArtProvider_GetBitmap(img, wx.ART_MENU, (16, 16))
				create_menu_item(wnd, menu, label, function, description, accel,
						wxid, img)
			elif len(item) == 5:
				label, accel, description, function, wxid = item
				create_menu_item(wnd, menu, label, function, description, accel, wxid)
			else:
				label, accel, description, function = item
				create_menu_item(wnd, menu, label, function, description, accel)

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
