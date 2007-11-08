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
__revision__	= '$Id: __init__.py 2 2006-12-24 21:07:13Z k $'



import sys
import time

import gettext
_ = gettext.gettext

import wx

from kpylibs.guitools	import create_button
from kpylibs.eventgenerator import EventGenerator


class InfoPanel(wx.Panel, EventGenerator):
	def __init__(self, *args, **kwargs):
		wx.Panel.__init__(self, *args, **kwargs)
		EventGenerator.__init__(self)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self._create_layout(), 1, wx.EXPAND)
		self.SetSizerAndFit(sizer)
		
		self._image = None
		self._folder = None
	
	
	def _create_layout(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_layout_page_main(notebook),	_('Main'))
		notebook.AddPage(self._create_layout_page_desc(notebook),	_('Description'))
		notebook.AddPage(self._create_layout_page_exif(notebook),	_('Exif'))
		notebook.AddPage(self._create_layout_page_folder(notebook),	_('Folder'))
		return notebook
		
		
	def _create_layout_page_main(self, parent):
		panel = wx.Panel(parent, -1)
		listctrl = self._listctrl_main = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(listctrl, 1, wx.EXPAND)
		panel.SetSizerAndFit(sizer)
		
		listctrl.InsertColumn(0, 'Tag')
		listctrl.InsertColumn(1, 'Value')
		
		return panel
		
		
	def _create_layout_page_desc(self, parent):
		panel = wx.Panel(parent, -1)
		
		textctrl = self._textctrl_desc = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
		button = create_button(panel, _('Save'), self._on_update_descr)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(textctrl, 1, wx.EXPAND)
		sizer.Add(button,0, wx.EXPAND|wx.ALL, 5)
		panel.SetSizerAndFit(sizer)
		
		return panel
		
		
	def _create_layout_page_exif(self, parent):
		panel = wx.Panel(parent, -1)
		
		listctrl = self._listctrl_exif = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
		
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(listctrl, 1, wx.EXPAND)
		panel.SetSizerAndFit(sizer)
		
		listctrl.InsertColumn(0, _('Tag'))
		listctrl.InsertColumn(1, _('Value'))
		
		return panel
	

	def _create_layout_page_folder(self, parent):
		panel = wx.Panel(parent, -1)
		
		listctrl = self._listctrl_folder = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
		textctrl = self._textctrl_folder_descr = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
		button	 = create_button(panel, _('Save'), self._on_update_folder_descr)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(listctrl, 1, wx.EXPAND)
		
		sizer.Add(wx.StaticText(panel, -1, _("Description")), 0, wx.EXPAND|wx.ALL, 5)
		subsizer = wx.BoxSizer(wx.HORIZONTAL)
		subsizer.Add(textctrl, 1, wx.EXPAND)
		subsizer.Add(button, 0, wx.EXPAND|wx.ALL, 5)
		sizer.Add(subsizer, 1, wx.EXPAND)
		panel.SetSizerAndFit(sizer)
		
		listctrl.InsertColumn(0, _('Tag'))
		listctrl.InsertColumn(1, _('Value'))
		
		return panel


	def _show_main(self, image):
		listctrl = self._listctrl_main
		
		def insert(key, val):
			idx = listctrl.InsertStringItem(sys.maxint, str(key))
			listctrl.SetStringItem(idx, 1, str(val))
			
		insert(_('Name'),	image.name)
		insert(_('Size'),	image.size)
		insert(_('Date'),	time.asctime(time.localtime(image.date)))
		insert(_('Tags'),	', '.join(image.tags))
			
		listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
	

	def _show_desc(self, image):
		self._textctrl_desc.SetValue(str(image.descr or ''))


	def _show_exif(self, image):
		listctrl = self._listctrl_exif
		for key, val in sorted(image.exif.items()):
			idx = listctrl.InsertStringItem(sys.maxint, str(key))
			listctrl.SetStringItem(idx, 1, str(val))
			
		listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		
		
	def _show_folder(self, folder):
		listctrl = self._listctrl_folder
		
		def insert(key, val):
			idx = listctrl.InsertStringItem(sys.maxint, str(key))
			listctrl.SetStringItem(idx, 1, str(val))
			
		insert(_('Name'),	folder.name)
		insert(_('Size'),	folder.size)
		insert(_('Date'),	time.asctime(time.localtime(folder.date)))
		insert(_('Tags'),	', '.join(folder.tags))
			
		listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		
		self._textctrl_folder_descr.SetValue(str(folder.descr or ""))


	def show(self, image):
		self.clear()
		self._image = image
		self._show_main(image)
		self._show_desc(image)
		self._show_exif(image)
		
		
	def show_folder(self, folder):
		self._folder = folder
		self._show_folder(folder)


	def clear(self):
		self._image = None
		self._listctrl_main.DeleteAllItems()
		self._listctrl_exif.DeleteAllItems()
		self._textctrl_desc.SetValue('')
		
		
	def clear_folder(self):
		self._folder is None
		self._listctrl_folder.DeleteAllItems()
		self._textctrl_folder_descr.SetValue('')
		
		
	def _on_update_descr(self, evt):
		if self._image is not None:
			new_descr = self._textctrl_desc.GetValue()
			if new_descr != self._image.descr:
				self._image.descr = new_descr
				self.event_call('update_image', self._image)


	def _on_update_folder_descr(self, evt):
		if self._folder is not None:
			new_descr = self._textctrl_folder_descr.GetValue()
			if new_descr != self._folder.descr:
				self._folder.descr = new_descr 
				self.event_call('update_folder', self._folder)



# vim: encoding=utf8: ff=unix: 
