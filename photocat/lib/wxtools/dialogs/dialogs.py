#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
"""
dialogs

KPyLibs
Copyright (c) Karol Będkowski, 2004, 2005, 2006

This file is part of KPyLibs

"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'

__all__ = ['dialog_file_save', 'dialog_file_load', 'dialog_get_text']


import wx


def dialog_file_save(parent, title, wildcard, filename=None, default_dir=None):
	if default_dir is None:
		dlg = wx.FileDialog(parent, title, style=wx.SAVE, wildcard=wildcard)
	else:
		dlg = wx.FileDialog(parent, title, style=wx.SAVE, wildcard=wildcard,
				defaultDir=default_dir)
	if filename is not None:
		dlg.SetPath(filename)
	if dlg.ShowModal() == wx.ID_OK:
		filename = dlg.GetPath()
	else:
		filename = None
	dlg.Destroy()
	return filename


def dialog_file_load(parent, title, wildcard, filename=None, must_exists=True,
		default_dir=None):
	flags = wx.OPEN
	if must_exists:
		flags |= wx.FILE_MUST_EXIST
	if default_dir is None:
		dlg = wx.FileDialog(parent, title, style=flags, wildcard=wildcard)
	else:
		dlg = wx.FileDialog(parent, title, style=flags, wildcard=wildcard,
				defaultDir=default_dir)
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
