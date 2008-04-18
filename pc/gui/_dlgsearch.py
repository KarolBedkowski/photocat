#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
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

__all__			= ['DlgProperties']


import sys

import logging
_LOG = logging.getLogger(__name__)

import wx

from kpylibs.guitools		import create_button
from kpylibs.iconprovider	import IconProvider
from kpylibs.appconfig		import AppConfig
from kpylibs				import dialogs

from pc.model		import Catalog, Directory, Disk, FileImage

_ = wx.GetTranslation



class DlgSearch(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent, catalogs):
		wx.Dialog.__init__(self, parent, -1, _('Find'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE|wx.FULL_REPAINT_ON_RESIZE )

		self._catalogs	= catalogs
		self._parent	= parent
		self._result	= []

		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['image', wx.ART_FOLDER])

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_fields(),	0, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self._create_layout_adv_search(),	0, wx.EXPAND|wx.ALL, 5)		
		main_grid.Add(self._create_layout_list(),	1, wx.EXPAND|wx.ALL, 5)

		self._statusbar = wx.StatusBar(self, -1)
		main_grid.Add(self._statusbar, 0, wx.EXPAND)

		self.SetSizerAndFit(main_grid)

		appconfig = AppConfig()
		size = appconfig.get('search_wnd', 'size', (400, 400))
		self.SetSize(size)
		
		position = appconfig.get('search_wnd', 'position')
		if position is None:
			self.Centre(wx.BOTH)
		else:
			self.Move(position)
		
		self.Bind(wx.EVT_CLOSE, self._on_close)


	def _create_layout_fields(self):
		grid = wx.FlexGridSizer(1, 3, 2, 2)
		grid.AddGrowableCol(1)
		grid.Add(wx.StaticText(self, -1, _('Text')), 0, wx.EXPAND|wx.ALL, 5)

		last = AppConfig().get_items('last_search')
		if last is None:
			last = []
		else:
			last = [l[1] for l in last]

		self._tc_text = wx.ComboBox(self, -1, choices=last)
		grid.Add(self._tc_text, 1, wx.EXPAND)
		button = create_button(self, _('Find'), self._on_btn_find)
		button.SetDefault()
		grid.Add(button, 0, wx.EXPAND)
		return grid


	def _create_layout_list(self):
		listctrl = self._result_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
		listctrl.SetImageList(self._icon_provider.get_image_list(), wx.IMAGE_LIST_SMALL)
		listctrl.InsertColumn(0, _('Name'))
		listctrl.InsertColumn(1, _('Catalog'))
		listctrl.InsertColumn(2, _('Disk'))
		listctrl.InsertColumn(3, _('Path'))
		
		listctrl.SetMinSize((350, 200))

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_activate, listctrl)

		return listctrl
	

	def _create_layout_adv_search(self):
		cp = self._cpanel = wx.CollapsiblePane(self, label=_("Advanced"))
		self._create_pane_adv_search(cp.GetPane())
		
		self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self._on_panel_advsearch_changed, cp)
		
		return cp


	def _create_pane_adv_search(self, pane):
		sizer = wx.BoxSizer()

		subsizer1 = wx.BoxSizer(wx.HORIZONTAL)

		box = wx.StaticBox(pane, -1, _("Search in"))
		bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
		cb = self._cb_search_in_names = wx.CheckBox(pane, -1, _("names"))
		cb.SetValue(True)
		bsizer.Add(cb, 0, wx.EXPAND|wx.ALL, 5)
		bsizer.Add((10, 10))
		cb = self._cb_search_in_descrs = wx.CheckBox(pane, -1, _("descriptions"))
		cb.SetValue(True)
		bsizer.Add(cb, 0, wx.EXPAND|wx.ALL, 5)
		bsizer.Add((10, 10))
		cb = self._cb_search_in_tags = wx.CheckBox(pane, -1, _("tags"))
		cb.SetValue(True)
		bsizer.Add(cb, 0, wx.EXPAND|wx.ALL, 5)
		subsizer1.Add(bsizer, 0, wx.EXPAND|wx.ALL, 5)

		box = wx.StaticBox(pane, -1, _("Search for"))
		bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
		cb = self._cb_search_for_files = wx.CheckBox(pane, -1, _("files"))
		cb.SetValue(True)
		bsizer.Add(cb, 0, wx.EXPAND|wx.ALL, 5)
		bsizer.Add((10, 10))
		cb = self._cb_search_for_dirs = wx.CheckBox(pane, -1, _("dirs"))
		cb.SetValue(True)
		bsizer.Add(cb, 0, wx.EXPAND|wx.ALL, 5)
		subsizer1.Add(bsizer, 0, wx.EXPAND|wx.ALL, 5)
		
		box = wx.StaticBox(pane, -1, _("Catalog"))
		bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
		cb = self._sb_search_in_catalog = wx.ComboBox(pane, -1, _("<all>"), choices=[_("<all>")], style=wx.CB_READONLY)
		[ cb.Append(cat.name) for cat in self._catalogs ]
		bsizer.Add(cb, 0, wx.EXPAND|wx.ALL, 5)
		subsizer1.Add(bsizer, 0, wx.EXPAND|wx.ALL, 5)

		sizer.Add(subsizer1, 0, wx.EXPAND)
		pane.SetSizer(sizer)


	#########################################################################
	
	
	def _get_options(self):
		options = None
		if self._cpanel.IsExpanded():
			options = {}
			names = self._cb_search_in_names.IsChecked()
			descr = self._cb_search_in_descrs.IsChecked()
			tags = self._cb_search_in_tags.IsChecked()
			if not(names == descr and names == tags):
				options['search_in_names'] = names
				options['search_in_descr'] = descr
				options['search_in_tags'] = tags
			
			files = self._cb_search_for_files.IsChecked()
			dirs = self._cb_search_for_dirs.IsChecked()
			if files != dirs:
				options['search_for_files'] = files
				options['search_for_dirs'] = dirs
				
			options['search_in_catalog'] = self._sb_search_in_catalog.GetValue()

		return options
	
	
	#########################################################################


	def _on_btn_find(self, evt):
		what = self._tc_text.GetValue().strip()
		if len(what) == 0:
			return

		what = what.lower()

		_LOG.debug('DlgSearch._on_btn_find: "%s"' % what)
		last_search_text_ctrl = self._tc_text

		last = [what] + [ text 
				for text 
				in (last_search_text_ctrl.GetString(idx) 
						for idx 
						in xrange(min(last_search_text_ctrl.GetCount(), 10))
				)
				if text != what
		]
		
		AppConfig().set_items('last_search', 'text', last)
		self._tc_text.Clear()
		[ self._tc_text.Append(text) for text in last ]
		self._tc_text.SetValue(what)

		listctrl = self._result_list
		listctrl.DeleteAllItems()

		icon_folder_idx	= self._icon_provider.get_image_index(wx.ART_FOLDER)
		icon_image_idx	= self._icon_provider.get_image_index('image')

		self._result = []
		counters = [0, 0]

		def insert(item):
			if isinstance(item, FileImage):
				ico = icon_image_idx
				counters[0] += 1
			else:
				ico = icon_folder_idx
				counters[1] += 1
			idx = listctrl.InsertImageStringItem(sys.maxint, str(item.name), ico)
			listctrl.SetStringItem(idx, 1, str(item.catalog.name))
			listctrl.SetStringItem(idx, 2, str(item.disk.name))
			listctrl.SetStringItem(idx, 3, item.path)
			listctrl.SetItemData(idx, len(self._result))
			self._result.append(item)

		options = self._get_options()
		_LOG.debug('DlgSearch._on_btn_find options: %r' % options)
		
		catalogs_to_search = self._catalogs
		if options is not None:
			search_in_catalog = options.get('search_in_catalog', _("<all>"))
			if search_in_catalog != _("<all>"):
				catalogs_to_search = [cat for cat in self._catalogs if cat.name == search_in_catalog ]
		
		for catalog in catalogs_to_search:
			result = catalog.check_on_find(what, options)
			[ insert(item) for item in result ]

		listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(3, wx.LIST_AUTOSIZE)

		if len(self._result) == 0:
			dialogs.message_box_info(self, _('Not found'), _('PC'))

		self._statusbar.SetStatusText(_('Found %d folders and %d files') % (counters[1], counters[0]))


	def _on_list_activate(self, evt):
		listctrl = self._result_list
		if listctrl.GetSelectedItemCount() > 0:
			index	= listctrl.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			itemidx	= listctrl.GetItemData(index)
			item	= self._result[itemidx]

			if isinstance(item, Directory) or isinstance(item, Disk):
				self._parent.show_item(item)
			elif isinstance(item, FileImage):
				self._parent.show_item(item.parent)


	def _on_close(self, evt):
		appconfig = AppConfig()
		appconfig.set('search_wnd', 'size',		self.GetSizeTuple())
		appconfig.set('search_wnd', 'position',	self.GetPositionTuple())

		evt.Skip()

	
	def _on_panel_advsearch_changed(self, evt):
		# hack na win32
		self.Refresh()



# vim: encoding=utf8: ff=unix:
