#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = '2010-06-09'

__all__ = ['DlgStats', 'PanelStats']


import logging
import locale

import wx
import wx.lib.mixins.listctrl as listmix

from photocat.stats import STATS_PROVIDERS
from photocat.lib.wxtools.iconprovider import IconProvider
from photocat.lib import hlplocale
from photocat.lib import hlpwx


_LOG = logging.getLogger(__name__)


class _StatsListCtrlPanel(wx.Panel, listmix.ColumnSorterMixin):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['image', wx.ART_FOLDER, 'sm_up', 'sm_down'])

		self._img_sm_up = self._icon_provider.get_image_index('sm_up')
		self._img_sm_dn = self._icon_provider.get_image_index('sm_down')

		self._create_list()
		self.itemDataMap = {}
		listmix.ColumnSorterMixin.__init__(self, 3)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._list, 1, wx.EXPAND)
		self.SetSizer(sizer)
		self.SetAutoLayout(True)

	def _create_list(self):
		self._list = list_ = wx.ListCtrl(self, -1,
				style=wx.LC_REPORT | wx.LC_SORT_ASCENDING)
		list_.SetImageList(self._icon_provider.image_list, wx.IMAGE_LIST_SMALL)

		list_.InsertColumn(0, _('Value'))
		list_.InsertColumn(1, _('Count'))
		list_.InsertColumn(2, _('%'))

	def GetListCtrl(self):
		return self._list

	def GetSortImages(self):
		return (self._img_sm_dn, self._img_sm_up)

	def fill(self, data):
		self._list.DeleteAllItems()
		self.itemDataMap.clear()
		if not data:
			return
		for idx, (value, number, perc) in enumerate(data):
			lidx = self._list.InsertStringItem(idx,
					hlplocale.from_locale(value[1]) or _('Unknown'))
			self._list.SetStringItem(lidx, 1, str(number))
			if perc is not None:
				self._list.SetStringItem(lidx, 2, locale.format('%0.1f',
						(perc * 100)))
			self._list.SetItemData(lidx, idx)
			self.itemDataMap[idx] = (value[0], number, perc)
		self._list.SetColumnWidth(0, 200)
		self._list.SetColumnWidth(1, 50)
		self._list.SetColumnWidth(2, 50)
		self.SortListItems(0, True)


class PanelStats(wx.Panel):
	def __init__(self, parent, data):
		wx.Panel.__init__(self, parent)

		self._data = data if hasattr(data, '__iter__') else (data, )
		self._curr_stats = {}
		self._stats_providers = None

		self._create_layout()
		self._fill_stats()

		self.Bind(wx.EVT_CHOICE, self._on_stats_provider_changed,
				self._cb_stats_providers)
		self.Bind(wx.EVT_LISTBOX, self._on_stats_changed, self._lb_stats)

	############################################################################

	def _create_layout(self):
		self._cb_stats_providers = wx.Choice(self, -1,
				choices=[_("Please select...")])
		self._lb_stats = wx.ListBox(self, -1, size=(170, -1),
				style=wx.LB_SINGLE | wx.LB_SORT)
		self._lc_result = _StatsListCtrlPanel(self)

		grid = wx.BoxSizer(wx.HORIZONTAL)
		grid.Add(wx.StaticText(self, -1, _('Statistic:')))
		grid.Add((6, 6))
		grid.Add(self._cb_stats_providers, 1, wx.EXPAND)

		grid_main = wx.BoxSizer(wx.VERTICAL)
		grid_main.Add(grid, 0, wx.EXPAND)
		grid_main.Add((6, 6))

		grid = wx.BoxSizer(wx.HORIZONTAL)
		grid.Add(self._lb_stats, 0, wx.EXPAND)
		grid.Add((6, 6))
		grid.Add(self._lc_result, 1, wx.EXPAND)
		grid_main.Add(grid, 1, wx.EXPAND)

		grid_panel = wx.BoxSizer(wx.VERTICAL)
		grid_panel.Add(grid_main, 1, wx.EXPAND | wx.ALL, 12)
		self.SetSizerAndFit(grid_panel)

	def _fill_stats(self):
		self._stats_providers = {}
		for sprov in STATS_PROVIDERS:
			self._cb_stats_providers.Append(sprov.name)
			self._stats_providers[sprov.name] = sprov()

	def _on_stats_provider_changed(self, evt):
		with hlpwx.with_wait_cursor():
			selection = self._cb_stats_providers.GetStringSelection()
			exst = self._cb_stats_providers.GetCount() > len(self._stats_providers)
			if exst and self._cb_stats_providers.GetSelection() == 0:
				return
			sprov = self._stats_providers[selection]
			if sprov.need_compute:
				dlg_progress = wx.ProgressDialog(_("Computing statistics..."),
						" " * 50, 20, parent=self, style=wx.PD_APP_MODAL)
				self._curr_stats = sprov.get_stats(self._data, dlg_progress.Pulse)
				dlg_progress.Destroy()
			else:
				self._curr_stats = sprov.get_stats(self._data)
			self._lb_stats.Clear()
			for key in self._curr_stats.iterkeys():
				self._lb_stats.Append(key)
			self._lb_stats.SetSelection(0)
			self._on_stats_changed(None)
			if exst:
				self._cb_stats_providers.Delete(0)
				self._cb_stats_providers.SetStringSelection(selection)

	def _on_stats_changed(self, evt):
		with hlpwx.with_wait_cursor():
			self._lc_result.Freeze()
			sel = self._lb_stats.GetStringSelection()
			self._lc_result.fill(self._curr_stats[sel] if sel else None)
			self._lc_result.Thaw()


class DlgStats(wx.Dialog):
	''' Dialog statystyk '''

	def __init__(self, parent, collections):
		collections = collections if hasattr(collections, '__iter__') \
				else (collections, )
		title = _('Statistics') if len(collections) > 1 else \
				_('Statistics for %s') % collections[0].name

		wx.Dialog.__init__(self, parent, -1, title,
				style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE)

		self._panel = PanelStats(self, collections)
		self.SetSize((600, 400))


# vim: encoding=utf8: ff=unix:
