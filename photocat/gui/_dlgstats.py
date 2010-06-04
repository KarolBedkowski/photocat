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


class _OptionsError(StandardError):
	pass


###############################################################################


class DlgStats(wx.Dialog):
	''' Dialog wyszukiwania '''

	def __init__(self, parent, collections, selected_item=None):
		wx.Dialog.__init__(self, parent, -1, _('Statistics'),
				style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE)

		self._collections = collections
		self._parent = parent
		self._selected_item = selected_item
		self._curr_stats = {}

		self._create_layout()
		self._fill_stats()

		self.Bind(wx.EVT_COMBOBOX, self._on_stats_provider_changed,
				self._cb_stats_providers)
		self.Bind(wx.EVT_LISTBOX, self._on_stats_changed, self._lb_stats)

	############################################################################

	def _create_layout(self):
		self._cb_stats_providers = wx.ComboBox(self, -1)
		self._lb_stats = wx.ListBox(self, -1, style=wx.LB_SINGLE | wx.LB_SORT)
		self._tc_result = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)

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
		grid.Add(self._tc_result, 2, wx.EXPAND)
		grid_main.Add(grid, 1, wx.EXPAND)

		grid_panel = wx.BoxSizer(wx.VERTICAL)
		grid_panel.Add(grid_main, 1, wx.EXPAND | wx.ALL, 12)
		self.SetSizerAndFit(grid_panel)

	def _fill_stats(self):
		for name in STATS_PROVIDERS.iterkeys():
			self._cb_stats_providers.Append(name)

	def _on_stats_provider_changed(self, evt):
		sprov = STATS_PROVIDERS[self._cb_stats_providers.GetValue()]
		self._curr_stats = dict(sprov().get_stats((self._collections, )))
		self._lb_stats.Clear()
		for key in self._curr_stats.iterkeys():
			self._lb_stats.Append(key)
		self._tc_result.SetValue('')

	def _on_stats_changed(self, evt):
		sel = self._lb_stats.GetStringSelection()
		print sel
		values = []
		for value, number, perc in self._curr_stats[sel]:
			if not value:
				value = _('unknown')
			values.append('%s: %0.1f%% (%d)' % (value, perc, number))
		self._tc_result.SetValue('\n'.join(values))



# vim: encoding=utf8: ff=unix:
