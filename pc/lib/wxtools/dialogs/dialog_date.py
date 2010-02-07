#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=W0401, C0103
"""
dialog_date

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

__all__ = ['DialogDate', 'dialog_get_date']



import wx
import wx.calendar



class DialogDate(wx.Dialog):
	def __init__(self, parent, date=None, caption='Wybierz date'):
		wx.Dialog.__init__(self, parent, -1, caption, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

		main_grid = wx.BoxSizer(wx.VERTICAL)

		self.__tc_data = wx.calendar.CalendarCtrl(self, -1, style=wx.calendar.CAL_MONDAY_FIRST)
		main_grid.Add(self.__tc_data, 1, wx.EXPAND)
		main_grid.Add(self.CreateButtonSizer(wx.OK|wx.CANCEL), 0, wx.EXPAND|wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.Centre(wx.BOTH)

		if date is not None and len(date) > 0:
			self.set_date(date)

		self.Bind(wx.calendar.EVT_CALENDAR, self.__on_cal_selected, self.__tc_data)

	def get_date(self):
		return self.__tc_data.GetDate().FormatISODate()

	def set_date(self, str_date):
		date = wx.DateTime()
		date.ParseDate(str_date)
		self.__tc_data.SetDate(date)

	def __on_cal_selected(self, evt):
		self.EndModal(wx.ID_OK)



def dialog_get_date(parent, date=None, caption='Wybierz date'):
	dlg = DialogDate(parent, date, caption)
	res = None
	if dlg.ShowModal() == wx.ID_OK:
		res = dlg.get_date()
	dlg.Destroy()
	return res


# vim: encoding=utf8:
