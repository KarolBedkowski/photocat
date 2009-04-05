#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
SearchResultListCtrl
 -- listctrl z sortowaniem dla wyników wyszukiwania

 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

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

__all__			= ['SearchResultListCtrl']


import sys
import time
import logging
_LOG = logging.getLogger(__name__)

import wx
import wx.lib.mixins.listctrl  as  listmix

from kpylibs.formaters		import format_human_size

_ = wx.GetTranslation



class SearchResultListCtrl(wx.ListCtrl, listmix.ColumnSorterMixin):
	''' Kontrolka listy wyników wyszukiwania z możliwością sortowania '''

	def __init__(self, *argv, **kwargv):
		wx.ListCtrl.__init__(self, *argv, **kwargv)
		listmix.ColumnSorterMixin.__init__(self, 6)

		self._icons = (-1, -1)
		self.clear()

		self.InsertColumn(0, _('Name'))
		self.InsertColumn(1, _('Catalog'))
		self.InsertColumn(2, _('Disk'))
		self.InsertColumn(3, _('Path'))
		self.InsertColumn(4, _('File date'))
		self.InsertColumn(5, _('File size'))


	def clear(self):
		self.itemDataMap = []
		self.DeleteAllItems()


	###########################################################################################


	def _get_result(self):
		return self.itemDataMap

	def _set_result(self, result):
		self.itemDataMap = result

	result = property(_get_result, _set_result)


	###########################################################################################


	def set_sort_icons(self, up, down):
		''' srlc.set_sort_icons(up, down) -- ustawienie ikon dla pokazania sortowania '''
		self._icons = (down, up)


	def insert(self, item, index, show_size, ico):
		''' srlc.index(item, index, show_size, ico) -- wstawienie elementu '''

		idx = self.InsertImageStringItem(sys.maxint, str(item.name), ico)
		self.SetStringItem(idx, 1, str(item.catalog.name))
		self.SetStringItem(idx, 2, str(item.disk.name))
		self.SetStringItem(idx, 3, item.path)
		self.SetStringItem(idx, 4, time.strftime('%c', time.localtime(item.date)))
		if show_size:
			self.SetStringItem(idx, 5, format_human_size(item.size))

		self.SetItemData(idx, index)


	def autosize_cols(self):
		''' srlc.autosize_cols() -- autosize kolumn '''
		self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		self.SetColumnWidth(3, wx.LIST_AUTOSIZE)


	###########################################################################################

	def GetListCtrl(self):
		return self


	def GetColumnSorter(self):
		col = self._col
		ascending = 1 if self._colSortFlag[col] else -1

		sortfnc = {
			0: lambda x,y: cmp(self.itemDataMap[x].name.lower(), self.itemDataMap[y].name.lower()) * ascending,
			1: lambda x,y: cmp(self.itemDataMap[x].catalog.name.lower(), self.itemDataMap[y].catalog.name.lower()) * ascending,
			2: lambda x,y: cmp(self.itemDataMap[x].disk.name.lower(), self.itemDataMap[y].disk.name.lower()) * ascending,
			3: lambda x,y: cmp(self.itemDataMap[x].path.lower(), self.itemDataMap[y].path.lower()) * ascending,
			4: lambda x,y: cmp(self.itemDataMap[x].date, self.itemDataMap[y].date) * ascending,
			5: lambda x,y: cmp(self.itemDataMap[x].size, self.itemDataMap[y].size) * ascending
		}.get(col)

		return sortfnc


	def GetSortImages(self):
		return self._icons





# vim: encoding=utf8: ff=unix:
