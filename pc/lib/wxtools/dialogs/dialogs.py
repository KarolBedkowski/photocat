#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
"""
dialogs

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

__all__ = ['dialog_file_save', 'dialog_file_load', 'dialog_get_text']


import wx



def dialog_file_save(parent, title, wildcard, filename=None, default_dir=None):
	if default_dir is None:
		dlg = wx.FileDialog(parent, title, style=wx.SAVE|wx.OVERWRITE_PROMPT, wildcard=wildcard)
	else:
		dlg = wx.FileDialog(parent, title, style=wx.SAVE|wx.OVERWRITE_PROMPT, wildcard=wildcard, defaultDir=default_dir)
	if filename is not None:
		dlg.SetPath(filename)
	if dlg.ShowModal() == wx.ID_OK:
		filename = dlg.GetPath()
	else:
		filename = None
	dlg.Destroy()
	return filename


def dialog_file_load(parent, title, wildcard, filename=None, must_exists=True, default_dir=None):
	flags = wx.OPEN
	if must_exists:
		flags |= wx.FILE_MUST_EXIST
	if default_dir is None:
		dlg = wx.FileDialog(parent, title, style=flags, wildcard=wildcard)
	else:
		dlg = wx.FileDialog(parent, title, style=flags, wildcard=wildcard, defaultDir=default_dir)
	if filename is not None:
		dlg.SetPath(filename)
	if dlg.ShowModal() == wx.ID_OK:
		filename = dlg.GetPath()
	else:
		filename = None
	dlg.Destroy()
	return filename


def dialog_get_text(parent, title, message, value=''):
	dlg = wx.TextEntryDialog(parent, message, title, value)
	if dlg.ShowModal() == wx.ID_OK:
		result = dlg.GetValue()
	else:
		result = None
	dlg.Destroy()
	return result

# vim: encoding=utf8:
