#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2014

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2014'
__revision__ = '$Id$'

__all__ = ['DlgProperties']


import sys
import logging

import wx
import wx.lib.buttons as buttons
import wx.lib.foldpanelbar as fpb

from photocat.model import Collection, Directory, Disk, FileImage
from photocat.engine import search, image
from photocat.lib.singleton import Singleton
from photocat.lib.appconfig import AppConfig
from photocat.lib.wxtools import dialogs
from photocat.lib.wxtools.guitools import create_button
from photocat.lib.wxtools.iconprovider import IconProvider
from photocat.gui._dlgproperties import DlgProperties

from components.thumbctrl import ThumbCtrl, EVT_THUMB_DBCLICK, \
	EVT_THUMB_SELECTION_CHANGE
from components.searchresultlistctrl import SearchResultListCtrl


_LOG = logging.getLogger(__name__)


###############################################################################


class _OptionsError(StandardError):
	pass


###############################################################################


class _DlgSearch(wx.Frame):
	''' Dialog wyszukiwania '''

	def __init__(self, parent, collections, selected_item=None):
		wx.Frame.__init__(self, parent, -1, _('Search'),
				style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)

		self._collections = collections
		self._parent = parent
		self._result = []
		self._selected_item = selected_item
		self._sort_order = None
		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['image', wx.ART_FOLDER, 'sm_up', 'sm_down'])

		self._create_layout()

		self.Bind(wx.EVT_CLOSE, self._on_close)

	############################################################################

	def _create_layout(self):
		spittwnd = wx.SplitterWindow(self, -1,
				style=wx.SP_LIVE_UPDATE | wx.SW_BORDER)
		spittwnd.SplitVertically(self._create_panel_left(spittwnd),
				self._create_layout_result(spittwnd), 100)
		spittwnd.SetMinimumPaneSize(200)

		self._statusbar = wx.StatusBar(self, -1)
		self._statusbar.SetFieldsCount(2)
		self._statusbar.SetStatusWidths([-1, 50])
		self.SetStatusBar(self._statusbar)

		appconfig = AppConfig()
		size = appconfig.get('search_wnd', 'size', (640, 480))
		self.SetMinSize((640, 480))
		self.SetSize(size)

		position = appconfig.get('search_wnd', 'position')
		if position is None:
			self.Centre(wx.BOTH)
		else:
			self.Move(position)

		self._thumb_width = appconfig.get('settings', 'thumb_width', 200)
		self._thumb_height = appconfig.get('settings', 'thumb_height', 200)
		self._thumbctrl.set_thumb_size(self._thumb_width, self._thumb_height)
		self._thumbctrl.thumbs_preload = appconfig.get('settings',
				'view_preload', True)

		self._tc_text.SetFocus()
		spittwnd.SetSashPosition(appconfig.get('settings', 'thumb_width',
			200) + 24)

	def _create_panel_left(self, parent):
		cbs = fpb.CaptionBarStyle()
		cbs.SetCaptionStyle(fpb.CAPTIONBAR_RECTANGLE)

		panel = wx.Panel(parent, -1)
		grid = wx.BoxSizer(wx.VERTICAL)

		pnl = fpb.FoldPanelBar(panel, -1, wx.DefaultPosition, wx.Size(200, -1))
		self._create_layout_fields(pnl, cbs)
		self._create_layout_options(pnl, cbs)
		self._create_layout_advanced(pnl, cbs)
		self._create_layout_preview(pnl, cbs)
		self._create_layout_info(pnl, cbs)

		grid.Add(pnl, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 12)
		panel.SetSizerAndFit(grid)

		return panel

	def _create_layout_fields(self, parent, cbs):
		item = parent.AddFoldPanel(_('Search'), collapsed=False, cbstyle=cbs)
		self._tc_text = wx.SearchCtrl(item, style=wx.TE_PROCESS_ENTER)
		#wx.ComboBox(item, -1, choices=search.get_last_search())
		parent.AddFoldPanelWindow(item, self._tc_text, fpb.FPB_ALIGN_WIDTH, 5)

		parent.AddFoldPanelWindow(item, wx.Panel(item, -1, size=(12, 12)),
				fpb.FPB_ALIGN_WIDTH, 5)

		self._make_last_search_menu()

		self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self._on_btn_find, self._tc_text)
		self.Bind(wx.EVT_TEXT_ENTER, self._on_btn_find, self._tc_text)

		return item

	def _create_layout_advanced(self, parent, cbs):
		item = parent.AddFoldPanel(_('Advanced'), collapsed=True, cbstyle=cbs)
		self._cpanel = item
		parent.AddFoldPanelWindow(item, wx.StaticText(item, -1,
				_('Search in fields:')), fpb.FPB_ALIGN_WIDTH, 5)

		def add(name):
			cb = wx.CheckBox(item, -1, name)
			cb.SetValue(True)
			parent.AddFoldPanelWindow(item, cb, fpb.FPB_ALIGN_WIDTH, 5, 12)
			return cb

		self._cb_search_in_names = add(_("names"))
		self._cb_search_in_descrs = add(_("descriptions"))
		self._cb_search_in_tags = add(_("tags"))

		parent.AddFoldPanelSeparator(item)

		# szukanie plików/katalogów
		parent.AddFoldPanelWindow(item, wx.StaticText(item, -1,
				_('Search for:')), fpb.FPB_ALIGN_WIDTH, 5)

		panel = wx.Panel(item, -1)
		box = wx.BoxSizer(wx.HORIZONTAL)
		self._cb_search_for_files = wx.CheckBox(panel, -1, _("files"))
		self._cb_search_for_files.SetValue(True)
		box.Add(self._cb_search_for_files, 1, wx.EXPAND)
		box.Add((5, 5))
		self._cb_search_for_dirs = wx.CheckBox(panel, -1, _("dirs"))
		self._cb_search_for_dirs.SetValue(True)
		box.Add(self._cb_search_for_dirs, 1, wx.EXPAND)

		panel.SetSizerAndFit(box)
		parent.AddFoldPanelWindow(item, panel, fpb.FPB_ALIGN_WIDTH, 2, 24)

		parent.AddFoldPanelSeparator(item)

		# szukanie w ...
		parent.AddFoldPanelWindow(item, wx.StaticText(item, -1,
				_('Search in disks/collections:')), fpb.FPB_ALIGN_WIDTH, 5)
		cb = self._sb_search_in_collection = wx.ComboBox(item, -1, _("<all>"),
				choices=[_("<all>")], style=wx.CB_READONLY)
		parent.AddFoldPanelWindow(item, cb, fpb.FPB_ALIGN_WIDTH, 5, 12)

		if self._selected_item is not None:
			if isinstance(self._selected_item, Disk):
				map(cb.Append, (_("<current collection>"), _("<current disk>")))
			elif isinstance(self._selected_item, Directory):
				map(cb.Append, (_("<current collection>"), _("<current disk>"),
						_("<current dir>")))
			elif isinstance(self._selected_item, Collection) and \
					len(self._collections) > 1:
				map(cb.Append, (_("<current collection>"), _("<current disk>")))

		for cat in self._collections:
			cb.Append(_("collection: %s") % cat.name)

		parent.AddFoldPanelSeparator(item)

		# szukanie wg dat
		self._cb_date = wx.CheckBox(item, -1, _("Search by date"))
		parent.AddFoldPanelWindow(item, self._cb_date, fpb.FPB_ALIGN_WIDTH, 5)

		panel = wx.Panel(item, -1)
		box = wx.FlexGridSizer(2, 2, 5, 12)
		box.Add(wx.StaticText(panel, -1, _('begin:')), 0, wx.ALIGN_CENTER_VERTICAL)

		self._dp_start_date = wx.DatePickerCtrl(panel, size=(120, -1),
				style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.SUNKEN_BORDER)
		box.Add(self._dp_start_date)

		box.Add(wx.StaticText(panel, -1, _('end:')), 0, wx.ALIGN_CENTER_VERTICAL)
		self._dp_stop_date = wx.DatePickerCtrl(panel, size=(120, -1),
				style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.SUNKEN_BORDER)
		box.Add(self._dp_stop_date)

		panel.SetSizerAndFit(box)
		parent.AddFoldPanelWindow(item, panel, fpb.FPB_ALIGN_LEFT, 5, 12)

		parent.AddFoldPanelWindow(item, wx.Panel(item, -1, size=(12, 12)),
				fpb.FPB_ALIGN_WIDTH, 5)
		return item

	def _create_layout_options(self, parent, cbs):
		item = parent.AddFoldPanel(_('Options'), collapsed=True, cbstyle=cbs)

		self._cb_regex = wx.CheckBox(item, -1, _("Regular expression"))
		parent.AddFoldPanelWindow(item, self._cb_regex, fpb.FPB_ALIGN_WIDTH)

		self._cb_match_case = wx.CheckBox(item, -1, _("Match case"))
		parent.AddFoldPanelWindow(item, self._cb_match_case, fpb.FPB_ALIGN_WIDTH)

		parent.AddFoldPanelWindow(item, wx.Panel(item, -1, size=(12, 12)),
				fpb.FPB_ALIGN_WIDTH, 2, 12)
		return item

	def _create_layout_result(self, parent):
		panel = wx.Panel(parent, -1)
		self._grid_result = grid = wx.BoxSizer(wx.VERTICAL)

		grid.Add(self._create_layout_list(panel), 1, wx.EXPAND | wx.ALL, 12)
		grid.Add(self._create_layout_thumbctrl(panel), 1, wx.EXPAND | wx.ALL, 12)

		grid_btns = wx.BoxSizer(wx.HORIZONTAL)

		self._btn_icons = buttons.GenToggleButton(panel, -1, _('Icons'))
		self._btn_icons.Enable(False)
		grid_btns.Add(self._btn_icons)
		self.Bind(wx.EVT_BUTTON, self._on_btn_icons, self._btn_icons)

		grid_btns.Add((5, 1), 1, wx.EXPAND)

		self._btn_properties = create_button(panel, None,
				self._on_btn_properties, wx.ID_PROPERTIES)
		self._btn_properties.Enable(False)
		grid_btns.Add(self._btn_properties)

		grid_btns.Add((5, 1))

		self._btn_goto = create_button(panel, _("Go to..."), self._on_btn_goto)
		self._btn_goto.Enable(False)
		grid_btns.Add(self._btn_goto)

		grid_btns.Add((5, 1), 1, wx.EXPAND)

		grid_btns.Add(create_button(panel, None, self._on_btn_close,
				wx.ID_CLOSE))

		grid.Add(grid_btns, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
				12)

		panel.SetSizerAndFit(grid)

		return panel

	def _create_layout_preview(self, parent, cbs):
		item = parent.AddFoldPanel(_('Preview'), collapsed=False, cbstyle=cbs)

		self._bmp_preview = wx.StaticBitmap(item, -1)
		appconfig = AppConfig()
		size = (appconfig.get('settings', 'thumb_width', 200),
				appconfig.get('settings', 'thumb_height', 200))
		self._bmp_preview.SetSize(size)
		self._bmp_preview.SetMinSize(size)

		parent.AddFoldPanelWindow(item, self._bmp_preview, fpb.FPB_ALIGN_WIDTH,
				2, 12)
		return item

	def _create_layout_info(self, parent, cbs):
		item = parent.AddFoldPanel(_('Info'), collapsed=True, cbstyle=cbs)
		self._image_info = wx.ListCtrl(item, -1, size=(-1, 250),
				style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.SUNKEN_BORDER)
		self._image_info.InsertColumn(0, '')
		self._image_info.InsertColumn(1, '')
		parent.AddFoldPanelWindow(item, self._image_info, fpb.FPB_ALIGN_WIDTH)
		return item

	def _create_layout_list(self, parent):
		listctrl = self._result_list = SearchResultListCtrl(parent, -1,
				style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		listctrl.SetImageList(self._icon_provider.image_list,
				wx.IMAGE_LIST_SMALL)
		listctrl.set_sort_icons(self._icon_provider.get_image_index('sm_up'),
				self._icon_provider.get_image_index('sm_down'))

		listctrl.SetMinSize((200, 200))

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_activate, listctrl)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_list_item_selected,
				listctrl)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_list_item_deselected,
				listctrl)

		return listctrl

	def _create_layout_thumbctrl(self, parent):
		self._thumbctrl = ThumbCtrl(parent, status_wnd=self)
		self._thumbctrl.Hide()

		self._thumbctrl.Bind(EVT_THUMB_SELECTION_CHANGE,
				self._on_thumb_sel_changed)
		self._thumbctrl.Bind(EVT_THUMB_DBCLICK, self._on_thumb_dclick)

		return self._thumbctrl

	#########################################################################

	def _get_options(self):
		options = None
		if self._cpanel.IsExpanded():
			options = {}
			names = self._cb_search_in_names.IsChecked()
			descr = self._cb_search_in_descrs.IsChecked()
			tags = self._cb_search_in_tags.IsChecked()
			if not (names == descr and names == tags):
				options['search_in_names'] = names
				options['search_in_descr'] = descr
				options['search_in_tags'] = tags

			files = self._cb_search_for_files.IsChecked()
			dirs = self._cb_search_for_dirs.IsChecked()
			if files != dirs:
				options['search_for_files'] = files
				options['search_for_dirs'] = dirs

			options['search_in_collection'] = self._sb_search_in_collection.GetValue()

			search_date = options['search_date'] = self._cb_date.IsChecked()
			if search_date:
				options['search_date_start'] = \
					self._dp_start_date.GetValue().GetTicks()
				options['search_date_end'] = \
						self._dp_stop_date.GetValue().GetTicks() + 86399

				if options['search_date_start'] > options['search_date_end']:
					raise _OptionsError(_("Wrong date range!"))

			options['opt_regex'] = self._cb_regex.GetValue()
			options['opt_match_case'] = self._cb_match_case.GetValue()

		return options

	def _make_last_search_menu(self, items=None):
		self._last_text_menu = menu = wx.Menu()
		for txt in (items or search.get_last_search()):
			self.Bind(wx.EVT_MENU, self._on_last_text_menu, menu.Append(-1, txt))

		self._tc_text.SetMenu(menu)

	#########################################################################

	def _on_btn_find(self, evt):
		what = self._tc_text.GetValue().strip()
		if len(what) == 0:
			return

		self._btn_properties.Enable(False)
		self._btn_goto.Enable(False)

		try:
			options = self._get_options()
			_LOG.debug('DlgSearch._on_btn_find options: %r', options)
		except _OptionsError, err:
			dialogs.message_box_info(self, _("Bad options:\n%s") % err, _('Find'))
			return

		listctrl = self._result_list
		listctrl.Freeze()
		listctrl.clear()

		self._btn_icons.SetValue(False)
		self._show_icons(False)

		icon_folder_idx = self._icon_provider.get_image_index(wx.ART_FOLDER)
		icon_image_idx = self._icon_provider.get_image_index('image')

		result = self._result = []
		counters = [0, 0]

		def insert(item):
			if isinstance(item, FileImage):
				ico = icon_image_idx
				counters[0] += 1
			else:
				ico = icon_folder_idx
				counters[1] += 1

			listctrl.insert(item, len(self._result), (ico == icon_image_idx),
					ico)
			result.append(item)

		collections, subdirs_count = search.get_collections_to_search(
				self._collections, options, self._selected_item)

		dlg_progress = wx.ProgressDialog(_("Searching..."), "\n",
				parent=self, maximum=subdirs_count + 1,
				style=(wx.PD_APP_MODAL | wx.PD_REMAINING_TIME \
						| wx.PD_ELAPSED_TIME | wx.PD_AUTO_HIDE \
						| wx.PD_CAN_ABORT))

		def update_dlg_progress(name, cntr=[0, True, True]):
			""" aktualizacja progress bara w dlg """
			cntr[0] = cntr[0] + 1
			found = len(result)
			cont = dlg_progress.Update(cntr[0],
					_("%(msg)s\nFound: %(found)d") % dict(msg=name, found=found))[0]

			if cont and cntr[1] and found > 1000:
				if not dialogs.message_box_warning_yesno(self,
						_("Found more than 1000 items.\nContinue?"), _('Find')):
					cntr[2] = False
				cntr[1] = False
			return cont & cntr[2]

		what = search.find(what, options, collections, insert, update_dlg_progress)

		listctrl.result = result
		listctrl.autosize_cols()
		listctrl.Thaw()

		dlg_progress.Destroy()

		found = len(self._result) > 0
		if found:
			self.Layout()
		else:
			dialogs.message_box_info(self, _('Not found'), _('Find'))

		self._btn_icons.Enable(found)
		self._make_last_search_menu(search.update_last_search(what))
		self._statusbar.SetStatusText(
				_('Found %(folders)d folders and %(files)d files') %
				dict(folders=counters[1], files=counters[0]))

	def _on_btn_properties(self, evt):
		''' Wyświetlenie właściwości pliku '''
		# FIXME: po edycji powinno się aktualizować drzewo
		if self._thumbctrl.IsShown():
			item_idx, items_count = self._thumbctrl.selected_index
		else:
			item, item_idx = self._get_selected_result_item()
			items_count = len(self._result)

		while item_idx > -1:
			item = self._result[item_idx]
			show_next_prev = (item_idx > 0, item_idx < items_count - 1)
			dlg = DlgProperties(self, item, show_next_prev=show_next_prev)
			res = dlg.ShowModal()
			dlg.Destroy()

			if res == wx.ID_BACKWARD:
				item_idx -= 1
			elif res == wx.ID_FORWARD:
				item_idx += 1
			else:
				break

	def _on_btn_goto(self, evt):
		self._on_list_activate(None)

	def _on_list_activate(self, evt):
		item, item_idx = self._get_selected_result_item()
		if item is not None:
			if isinstance(item, Directory) or isinstance(item, Disk):
				self._parent.show_item(item)

			elif isinstance(item, FileImage):
				self._parent.show_item(item.parent)
				self._parent.select_item(item)

			self._parent.Raise()

	def _on_list_item_selected(self, evt):
		''' callback na zaznacznie rezultatu - wyświetlenie podglądu '''
		itemidx = evt.GetData()
		item = self._result[itemidx]
		self._btn_properties.Enable(True)
		self._btn_goto.Enable(True)
		self._show_preview(item)
		self._show_image_info(item)

	def _on_list_item_deselected(self, evt):
		''' callback na odznaczenie rezultatu - wyświetlenie pustego podglądu '''
		self._bmp_preview.SetBitmap(wx.EmptyImage(1, 1).ConvertToBitmap())
		self._btn_properties.Enable(False)
		self._btn_goto.Enable(False)

	def _on_close(self, evt):
		appconfig = AppConfig()
		appconfig.set('search_wnd', 'size', self.GetSizeTuple())
		appconfig.set('search_wnd', 'position', self.GetPositionTuple())
		evt.Skip()

	def _on_panel_advsearch_changed(self, evt):
		''' callback na zwinięcie/rozwinięcie panelu '''
		# trzeba przebudować layout po zwinięciu/rozwinięciu panelu
		self.Layout()
		evt.Skip()

	def _on_btn_icons(self, evt):
		self._show_icons(evt.GetIsDown())

	def _on_btn_close(self, evt):
		self.Close()

	def _on_thumb_sel_changed(self, evt):
		item = self._thumbctrl.selected_item
		self._btn_properties.Enable(item is not None)
		self._btn_goto.Enable(item is not None)
		self._show_preview(item)
		self._show_image_info(item)

	def _on_thumb_dclick(self, evt):
		item = self._thumbctrl.selected_item
		if item is not None:
			if isinstance(item, FileImage):
				self._parent.show_item(item.parent)

	def _on_last_text_menu(self, evt):
		text = self._last_text_menu.GetLabel(evt.GetId())
		self._tc_text.SetValue(text)

	##########################################################################

	def _get_selected_result_item(self):
		listctrl = self._result_list
		item = None
		itemidx = -1
		if listctrl.GetSelectedItemCount() > 0:
			index = listctrl.GetNextItem(-1, wx.LIST_NEXT_ALL,
					wx.LIST_STATE_SELECTED)
			itemidx = listctrl.GetItemData(index)
			item = self._result[itemidx]

		return item, itemidx

	def _show_image_info(self, item):
		listctrl = self._image_info
		listctrl.DeleteAllItems()

		if item is None:
			return

		for dummy, key, val in sorted(item.info):
			idx = listctrl.InsertStringItem(sys.maxint, str(key))
			listctrl.SetStringItem(idx, 1, str(val))

		listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

	def _show_preview(self, item):
		self._bmp_preview.SetBitmap(wx.EmptyImage(1, 1).ConvertToBitmap())
		self._bmp_preview.SetBitmap(image.load_bitmap_from_item_with_size(item,
				self._thumb_width, self._thumb_height, 1)[0])
		self._bmp_preview.Refresh()

	def _show_icons(self, icons):
		if icons and len(self._result) > 1000:
			# jeżeli ilość plików > 1000 - ostrzeżenie i pytania
			if not dialogs.message_box_warning_yesno(self,
					_('Number of files exceed 1000!\nShow %d files?')
					% len(self._result), _('Find')):
				self._btn_icons.SetToggle(False)
				return

		self._thumbctrl.Show(icons)
		self._result_list.Show(not icons)

		if icons:
			size = (1, 1)
		else:
			appconfig = AppConfig()
			size = (appconfig.get('settings', 'thumb_width', 200),
					appconfig.get('settings', 'thumb_height', 200))

		self._image_info.DeleteAllItems()

		if icons:
			self._thumbctrl.show_dir([item
					for item in self._result
					if isinstance(item, FileImage)])
			self._bmp_preview.SetBitmap(wx.EmptyImage(1, 1).ConvertToBitmap())
		else:
			self._thumbctrl.show_dir([])

		self._bmp_preview.SetMinSize(size)
		self._grid_result.RecalcSizes()
		self._btn_goto.Enable(False)
		self._btn_properties.Enable(False)

		# odznaczenie
		index = -1
		while True:
			index = self._result_list.GetNextItem(index, wx.LIST_NEXT_ALL,
					wx.LIST_STATE_SELECTED)
			if index == -1:
				break

			self._result_list.SetItemState(index, 0, wx.LIST_STATE_SELECTED)


###############################################################################


class DlgSearchProvider(Singleton):
	''' DlgSearchProvider() -- tworzy i zarządza dlg wyszukiwania '''

	def _init(self):
		self._dialogs = []

	def create(self, parent, collections, selected_item=None):
		''' DlgSearchProvider().create(parent, collections, [selected_item])
		-- tworzy nowy dlg

		@param parent 	- okno nadrzędne
		@param collection	- katalog (katalogi)
		@param selected_item - aktualnie wybrany element

		Tworzony dlg jest dodawany do listy.
		'''
		dlg = _DlgSearch(parent, collections, selected_item)
		dlg.Bind(wx.EVT_CLOSE, self._on_dialog_close)
		self._dialogs.append(dlg)
		return dlg

	def close_all(self):
		''' DlgSearchProvider().close_all() -- zamknięcie wszystkich okien '''
		for dlg in self._dialogs:
			dlg.Close(True)

		self._dialogs = []

	def _on_dialog_close(self, evt):
		''' dlgsearchprovider._on_dialog_close(evt) -- event na zamknięcie dlg
		Usuwa zamykany dlg z listy.
		'''
		self._dialogs.remove(evt.GetEventObject())
		evt.Skip()
