#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
"""
message_boxes

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


__all__ = ['message_box_error', 'message_box_info', 'message_box_question_yesno', 'message_box_warning_yesno', 
		'message_box_warning_yesnocancel']


import wx



def message_box_error(parent, msg, title):
	dlg = wx.MessageDialog(parent, str(msg), title, wx.OK|wx.CENTRE|wx.ICON_ERROR)
	dlg.ShowModal()
	dlg.Destroy()


def message_box_info(parent, msg, title):
	dlg = wx.MessageDialog(parent, str(msg), title, wx.OK|wx.CENTRE|wx.ICON_INFORMATION)
	dlg.ShowModal()
	dlg.Destroy()


def message_box_question_yesno(parent, msg, title):
	dlg = wx.MessageDialog(parent, msg, title, wx.YES_NO|wx.NO_DEFAULT|wx.CENTRE|wx.ICON_QUESTION)
	res = dlg.ShowModal()
	dlg.Destroy()
	return res == wx.ID_YES


def message_box_warning_yesno(parent, msg, title):
	dlg = wx.MessageDialog(parent, msg, title, wx.YES_NO|wx.NO_DEFAULT|wx.CENTRE|wx.ICON_WARNING)
	res = dlg.ShowModal()
	dlg.Destroy()
	return res == wx.ID_YES


def message_box_warning_yesnocancel(parent, msg, title):
	dlg = wx.MessageDialog(parent, msg, title, wx.YES_NO|wx.CANCEL|wx.YES_DEFAULT|wx.CENTRE|wx.ICON_WARNING)
	res = dlg.ShowModal()
	dlg.Destroy()
	return res



# vim: encoding=utf8:
