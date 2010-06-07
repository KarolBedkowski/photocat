#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__revision__ = '$Id$'

__all__ = ['DlgStats']


import logging

import wx

from photocat.stats import STATS_PROVIDERS


_LOG = logging.getLogger(__name__)


###############################################################################


class DlgStats(wx.Dialog):
	''' Dialog wyszukiwania '''

	def __init__(self, parent, collections, selected_item=None):
		self._collections = collections if hasattr(collections, '__iter__') \
				else (collections, )

		title = _('Statistics') if len(self._collections) > 1 else \
				_('Statistics for %s') % self._collections[0].name

		wx.Dialog.__init__(self, parent, -1, title,
				style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE)

		self._parent = parent
		self._selected_item = selected_item
		self._curr_stats = {}
		self._stats_providers = []

		self._create_layout()
		self._fill_stats()

		self.SetSize((600, 400))

		self.Bind(wx.EVT_COMBOBOX, self._on_stats_provider_changed,
				self._cb_stats_providers)
		self.Bind(wx.EVT_LISTBOX, self._on_stats_changed, self._lb_stats)

	############################################################################

	def _create_layout(self):
		self._cb_stats_providers = wx.ComboBox(self, -1, _("Please select..."),
				style=wx.CB_READONLY | wx.CB_DROPDOWN)
		self._lb_stats = wx.ListBox(self, -1, style=wx.LB_SINGLE | wx.LB_SORT)
		self._lc_result = self._create_result_list()

		grid = wx.BoxSizer(wx.HORIZONTAL)
		grid.Add(wx.StaticText(self, -1, _('Statistic:')))
		grid.Add((6, 6))
		grid.Add(self._cb_stats_providers, 1, wx.EXPAND)

		grid_main = wx.BoxSizer(wx.VERTICAL)
		grid_main.Add(grid, 0, wx.EXPAND)
		grid_main.Add((6, 6))

		grid = wx.BoxSizer(wx.HORIZONTAL)
		grid.Add(self._lb_stats, 1, wx.EXPAND)
		grid.Add((6, 6))
		grid.Add(self._lc_result, 2, wx.EXPAND)
		grid_main.Add(grid, 1, wx.EXPAND)

		grid_panel = wx.BoxSizer(wx.VERTICAL)
		grid_panel.Add(grid_main, 1, wx.EXPAND | wx.ALL, 12)
		self.SetSizerAndFit(grid_panel)

	def _create_result_list(self):
		lc_result = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
		lc_result.InsertColumn(0, _('Value'))
		lc_result.InsertColumn(1, _('%'))
		lc_result.InsertColumn(2, _('Count'))
		return lc_result

	def _fill_stats(self):
		self._stats_providers = {}
		for sprov in STATS_PROVIDERS:
			self._cb_stats_providers.Append(sprov.name)
			self._stats_providers[sprov.name] = sprov()

	def _on_stats_provider_changed(self, evt):
		sprov = self._stats_providers[self._cb_stats_providers.GetValue()]
		self._curr_stats = sprov.get_stats(self._collections)
		self._lb_stats.Clear()
		for key in self._curr_stats.iterkeys():
			self._lb_stats.Append(key)
		self._lb_stats.SetSelection(0)
		self._on_stats_changed(None)

	def _on_stats_changed(self, evt):
		sel = self._lb_stats.GetStringSelection()
		listctrl = self._lc_result
		listctrl.DeleteAllItems()
		if not sel:
			return
		for idx, (value, number, perc) in enumerate(self._curr_stats[sel]):
			listctrl.InsertStringItem(idx, value[1] or _('Unknown'))
			if perc is not None:
				listctrl.SetStringItem(idx, 1, '%0.1f%%' % (perc * 100))
			listctrl.SetStringItem(idx, 2, str(number))

		listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		listctrl.SetColumnWidth(2, wx.LIST_AUTOSIZE)


# vim: encoding=utf8: ff=unix:
