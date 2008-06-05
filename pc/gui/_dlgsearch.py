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

import cStringIO

import wx
import wx.lib.buttons  as  buttons

from kpylibs.guitools		import create_button
from kpylibs.iconprovider	import IconProvider
from kpylibs.appconfig		import AppConfig
from kpylibs				import dialogs

from pc.model		import Catalog, Directory, Disk, FileImage

from components.thumbctrl	import ThumbCtrl, EVT_THUMB_DBCLICK, EVT_THUMB_SELECTION_CHANGE

from _dlgproperties	import DlgProperties

_ = wx.GetTranslation



class _OptionsError(StandardError):
	pass



class DlgSearch(wx.Dialog):
	''' Dialog o programie '''

	def __init__(self, parent, catalogs):
		wx.Dialog.__init__(self, parent, -1, _('Find'), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)
		#|wx.FULL_REPAINT_ON_RESIZE

		self._catalogs	= catalogs
		self._parent	= parent
		self._result	= []

		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['image', wx.ART_FOLDER])

		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_fields(),	0, wx.EXPAND|wx.ALL, 5)
		main_grid.Add(self._create_layout_adv_search(),	0, wx.EXPAND|wx.ALL, 5)		
		main_grid.Add(self._create_layout_result(),	1, wx.EXPAND|wx.ALL, 5)

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
		grid.Add(wx.StaticText(self, -1, _('Text')), 0, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)

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
	

	def _create_layout_result(self):
		grid = wx.BoxSizer(wx.HORIZONTAL)
		grid.Add(self._create_layout_list(), 1, wx.EXPAND|wx.ALL, 5)
		grid.Add(self._create_layout_thumbctrl(), 1, wx.EXPAND|wx.ALL, 5)
		grid.Add(self._create_layout_preview(), 0, wx.EXPAND|wx.ALL, 5)
		return grid

	
	def _create_layout_preview(self):
		panel = self._panel_preview = wx.Panel(self, -1)
		grid = wx.BoxSizer(wx.VERTICAL)
		
		self._bmp_preview = wx.StaticBitmap(panel, -1)
		grid.Add(self._bmp_preview, 0, wx.EXPAND|wx.ALL, 5)
		
		self._btn_properties = create_button(panel, _("Properties"), self._on_btn_properties)
		grid.Add(self._btn_properties, 0, wx.EXPAND|wx.ALL, 5)
		
		self._btn_icons = buttons.GenToggleButton(panel, -1, _('Icons'))
		grid.Add(self._btn_icons, 0, wx.EXPAND|wx.ALL, 5)
		self.Bind(wx.EVT_BUTTON, self._on_btn_icons, self._btn_icons)

		panel.SetSizer(grid)
		panel.Show(False)
		
		appconfig = AppConfig()
		size = (appconfig.get('settings', 'thumb_width', 200), appconfig.get('settings', 'thumb_height', 200))		
		self._bmp_preview.SetMinSize(size)

		return panel


	def _create_layout_list(self):
		listctrl = self._result_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
		listctrl.SetImageList(self._icon_provider.get_image_list(), wx.IMAGE_LIST_SMALL)
		listctrl.InsertColumn(0, _('Name'))
		listctrl.InsertColumn(1, _('Catalog'))
		listctrl.InsertColumn(2, _('Disk'))
		listctrl.InsertColumn(3, _('Path'))
		
		listctrl.SetMinSize((200, 200))

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_activate, listctrl)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_item_selected, listctrl)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_list_item_deselected, listctrl)

		return listctrl
	

	def _create_layout_adv_search(self):
		cp = self._cpanel = wx.CollapsiblePane(self, label=_("Advanced"))
		self._create_pane_adv_search(cp.GetPane())
		
		self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self._on_panel_advsearch_changed, cp)
		
		return cp
	

	def _create_layout_thumbctrl(self):
		self._thumbctrl = ThumbCtrl(self)
		self._thumbctrl.Hide()
		
		self._thumbctrl.Bind(EVT_THUMB_SELECTION_CHANGE, self._on_thumb_sel_changed)
		self._thumbctrl.Bind(EVT_THUMB_DBCLICK, self._on_thumb_dclick)
		
		return self._thumbctrl


	def _create_pane_adv_search(self, pane):
		sizer = wx.BoxSizer(wx.VERTICAL)

		subsizer1 = wx.BoxSizer(wx.HORIZONTAL)

		# szukanie w opisach/nazwach/tagach
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

		# szukanie plików/katalogów
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
		
		# szukanie w katalogu
		box = wx.StaticBox(pane, -1, _("Catalog"))
		bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
		cb = self._sb_search_in_catalog = wx.ComboBox(pane, -1, _("<all>"), choices=[_("<all>")], style=wx.CB_READONLY)
		[ cb.Append(cat.name) for cat in self._catalogs ]
		bsizer.Add(cb, 0, wx.EXPAND|wx.ALL, 5)
		subsizer1.Add(bsizer, 0, wx.EXPAND|wx.ALL, 5)

		sizer.Add(subsizer1, 0, wx.EXPAND)
		
		##############################
		
		# szukanie wg dat		
		box = wx.StaticBox(pane, -1, _("Date"))
		bsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
		
		self._cb_date = wx.CheckBox(pane, -1, _("Search by date"))
		bsizer.Add(self._cb_date, 0, wx.EXPAND|wx.ALL, 5)
		bsizer.Add((10, 10))
		bsizer.Add(wx.StaticText(pane, -1, _("begin:")), 0, wx.ALIGN_CENTER_VERTICAL)
		self._dp_start_date = wx.DatePickerCtrl(pane, size=(120,-1), style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
		bsizer.Add(self._dp_start_date, 0, wx.EXPAND|wx.ALL, 5)		
		bsizer.Add((10, 10))
		bsizer.Add(wx.StaticText(pane, -1, _("end:")), 0, wx.ALIGN_CENTER_VERTICAL)
		self._dp_stop_date = wx.DatePickerCtrl(pane, size=(120,-1), style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY)
		bsizer.Add(self._dp_stop_date, 0, wx.EXPAND|wx.ALL, 5)
		
		sizer.Add(bsizer, 0, wx.EXPAND|wx.ALL, 5)
		
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
			
			search_date = options['search_date'] = self._cb_date.IsChecked()
			if search_date:
				options['search_date_start'] = self._dp_start_date.GetValue().GetTicks()
				options['search_date_end'] = self._dp_stop_date.GetValue().GetTicks() + 86399
				
				if options['search_date_start'] > options['search_date_end']:
					raise _OptionsError(_("Wrong date range!"))

		return options
	
	
	#########################################################################


	def _on_btn_find(self, evt):
		what = self._tc_text.GetValue().strip()
		
		self._panel_preview.Show(False)
		self._btn_properties.Enable(False)

		try:
			options = self._get_options()
			_LOG.debug('DlgSearch._on_btn_find options: %r' % options)
		except _OptionsError, err:
			dialogs.message_box_info(self, _("Bad options:\n%s") % err, _('PC'))
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
		else:
			self._panel_preview.Show(True)
			self.Layout()

		self._statusbar.SetStatusText(_('Found %d folders and %d files') % (counters[1], counters[0]))


	def _on_btn_properties(self, evt):
		''' Wyświetlenie właściwości pliku '''
		# FIXME: po edycji powinno się aktualizować drzewo
		if self._thumbctrl.IsShown():
			item = self._thumbctrl.selected_item
		else:
			item = self._get_selected_result_item()
		if item is not None:
			dlg = DlgProperties(self, item)
			dlg.ShowModal()
			dlg.Destroy()
		

	def _on_list_activate(self, evt):
		item = self._get_selected_result_item()
		if item is not None:
			if isinstance(item, Directory) or isinstance(item, Disk):
				self._parent.show_item(item)
			elif isinstance(item, FileImage):
				self._parent.show_item(item.parent)


	def _on_list_item_selected(self, evt):
		''' callback na zaznacznie rezultatu - wyświetlenie podglądu '''
		itemidx	= evt.GetData()
		item	= self._result[itemidx]
		if isinstance(item, FileImage):
			try:
				stream = cStringIO.StringIO(item.image)
				img		= wx.ImageFromStream(stream)
			except Exception, err:
				_LOG.exception('Show item %s error' % item.name)
				img = wx.EmptyImage(1, 1)
		else:
			img = wx.EmptyImage(1, 1)
			
		self._bmp_preview.SetBitmap(wx.EmptyImage(1, 1).ConvertToBitmap())
		self._bmp_preview.SetBitmap(img.ConvertToBitmap())
		self._bmp_preview.Refresh()
		self._btn_properties.Enable(True)
	

	def _on_list_item_deselected(self, evt):
		''' callback na odznaczenie rezultatu - wyświetlenie pustego podglądu '''		
		self._bmp_preview.SetBitmap(wx.EmptyImage(1, 1).ConvertToBitmap())
		self._btn_properties.Enable(False)


	def _on_close(self, evt):
		appconfig = AppConfig()
		appconfig.set('search_wnd', 'size',		self.GetSizeTuple())
		appconfig.set('search_wnd', 'position',	self.GetPositionTuple())

		evt.Skip()

	
	def _on_panel_advsearch_changed(self, evt):
		''' callback na zwinięcie/rozwinięcie panelu '''
		# trzeba przebudować layout po zwinięciu/rozwinięciu panelu
		self.Layout()
		
	def _on_btn_icons(self, evt):
		icons = evt.GetIsDown()
		self._thumbctrl.Show(icons)
		self._result_list.Show(not icons)
		self.Layout()

		if icons:
			self._thumbctrl.show_dir([item for item in self._result if isinstance(item, FileImage)])
			self._bmp_preview.SetBitmap(wx.EmptyImage(1, 1).ConvertToBitmap())
		else:
			self._thumbctrl.clear()


	def _on_thumb_sel_changed(self, evt):
		item = self._thumbctrl.selected_item
		self._btn_properties.Enable(item is not None)

	
	def _on_thumb_dclick(self, evt):
		item = self._thumbctrl.selected_item
		if item is not None:
			if isinstance(item, FileImage):
				self._parent.show_item(item.parent)
	
	
	##########################################################################


	def _get_selected_result_item(self):
		listctrl = self._result_list
		item = None
		if listctrl.GetSelectedItemCount() > 0:
			index	= listctrl.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
			itemidx	= listctrl.GetItemData(index)
			item	= self._result[itemidx]
		return item


# vim: encoding=utf8: ff=unix:
