#!/usr/bin/python2.4
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


import logging
_LOG = logging.getLogger(__name__)

import wx
import wx.lib.mixins.listctrl  as  listmix

_ = wx.GetTranslation



class SearchResultListCtrl(wx.ListCtrl, listmix.ColumnSorterMixin):
	def __init__(self, *argv, **kwargv):
		wx.ListCtrl.__init__(self, *argv, **kwargv)
		listmix.ColumnSorterMixin.__init__(self, 6)
		
		self.clear()


	def clear(self):
		self.itemDataMap = []

	
	###########################################################################################


	def _get_result(self):
		return self.itemDataMap

	def _set_result(self, result):
		self.itemDataMap = result
		
	result = property(_get_result, _set_result)

	
	###########################################################################################

	


	###########################################################################################

	def GetListCtrl(self):	
		return self

	
	def GetColumnSorter(self):
		col = self._col
		ascending = 1 if self._colSortFlag[col] else -1

		if col == 0:
			sortfnc = lambda x,y: cmp(self.itemDataMap[x].name, self.itemDataMap[y].name) * ascending
		elif col == 1:
			sortfnc = lambda x,y: cmp(self.itemDataMap[x].catalog.name, self.itemDataMap[y].catalog.name) * ascending
		elif col == 2:
			sortfnc = lambda x,y: cmp(self.itemDataMap[x].disk.name, self.itemDataMap[y].disk.name) * ascending
		elif col == 3:
			sortfnc = lambda x,y: cmp(self.itemDataMap[x].path, self.itemDataMap[y].path) * ascending
		elif col == 4:
			sortfnc = lambda x,y: cmp(self.itemDataMap[x].date, self.itemDataMap[y].date) * ascending
		elif col == 5:
			sortfnc = lambda x,y: cmp(self.itemDataMap[x].size, self.itemDataMap[y].size) * ascending
			
		return sortfnc	



# vim: encoding=utf8: ff=unix:
