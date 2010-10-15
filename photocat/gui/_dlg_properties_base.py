#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.x (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'

__all__ = ['DlgPropertiesBase']


import sys

import wx
from wx.lib import masked

from photocat.engine import image as eimage
from photocat.gui.components.tags_list_box import TagsListBox
from photocat.lib.appconfig import AppConfig
from photocat.lib.wxtools.guitools import create_button
from ._panel_osm_map import PanelOsmMap

_LABEL_FONT_STYLE = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
_LABEL_FONT_STYLE.SetWeight(wx.FONTWEIGHT_BOLD)


class DlgPropertiesBase(wx.Dialog):
	''' Dialog o programie '''
	_CONFIG_KEY = 'properties_wnd'

	def __init__(self, parent, item, readonly=False, title=None,
			show_next_prev=False):
		wx.Dialog.__init__(self, parent, -1, title or _('%s Properties') % item.name,
				style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE)
		self._item = item
		self.readonly = readonly
		self._show_next_prev = show_next_prev
		self._panel_map = None
		# lista zmienionych podczas edycji nazw tagów
		self.changed_tags = None
		self._create_layout()
		self._set_pos()
		self.Bind(wx.EVT_BUTTON, self._on_ok, id=wx.ID_OK)
		self.Bind(wx.EVT_BUTTON, self._on_close, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_CLOSE, self._on_close)

	@staticmethod
	def _create_label(parent, title):
		ctr = wx.StaticText(parent, -1, title)
		ctr.SetFont(_LABEL_FONT_STYLE)
		return ctr

	def _create_layout(self):
		main_grid = wx.BoxSizer(wx.VERTICAL)
		main_grid.Add(self._create_layout_notebook(), 1, wx.EXPAND | wx.ALL, 12)
		btns = wx.CANCEL
		if not self.readonly:
			btns |= wx.OK
		grid = self.CreateStdDialogButtonSizer(btns)
		if self._show_next_prev:
			btn_prev = create_button(self, None, self._on_btn_prev,
					wx.ID_BACKWARD)
			grid.Insert(0, btn_prev)
			grid.Insert(1, (10, 5))
			btn_next = create_button(self, None, self._on_btn_next,
					wx.ID_FORWARD)
			grid.Insert(2, btn_next)
			grid.Insert(3, (5, 5), 1, wx.EXPAND)
			prev, next = self._show_next_prev
			btn_prev.Enable(prev)
			btn_next.Enable(next)
		main_grid.Add(grid, 0, wx.EXPAND | wx.ALL, 12)
		self.SetSizerAndFit(main_grid)

	def _set_pos(self):
		appconfig = AppConfig()
		size = appconfig.get(self._CONFIG_KEY, 'size', (300, 300))
		self.SetSize(size)
		position = appconfig.get(self._CONFIG_KEY, 'position')
		if position is None:
			self.Centre(wx.BOTH)
		else:
			self.Move(position)

	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_layout_page_main(notebook), _('Main'))
		notebook.AddPage(self._create_layout_page_desc(notebook), _('Comment'))
		notebook.AddPage(self._create_layout_page_exif(notebook), _('Exif'))
		notebook.AddPage(self._create_layout_page_tags(notebook), _('Tags'))
		notebook.AddPage(self._create_layout_page_other(notebook), _('Other'))
		notebook.AddPage(self._create_layout_page_map(notebook), _('Map'))
		return notebook

	def _create_layout_page_main(self, parent):
		panel = wx.Panel(parent, -1)
		sizer = wx.BoxSizer(wx.VERTICAL)
		bsizer = wx.FlexGridSizer(2, 2, 5, 12)
		bsizer.AddGrowableCol(1)
		for dummy, key, val in sorted(self._item.info):
			if key == '':
				bsizer.Add((1, 5))
				bsizer.Add((1, 5))
			else:
				bsizer.Add(self._create_label(panel, key + ":"), 0,
						wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
				bsizer.Add(wx.StaticText(panel, -1, str(val)), 1, wx.EXPAND)
		sizer.Add(bsizer, 1, wx.ALL | wx.ALIGN_CENTER, 12)
		panel.SetSizerAndFit(sizer)
		return panel

	def _create_layout_page_desc(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._create_label(panel, _("Comment")))
		textctrl = self._textctrl_desc = wx.TextCtrl(panel, -1,
				style=wx.TE_MULTILINE)
		textctrl.SetEditable(not self.readonly)
		textctrl.SetValue(str(self._item.desc or ''))
		sizer.Add(textctrl, 1, wx.EXPAND | wx.LEFT | wx.TOP, 12)
		panel_sizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)

		return panel

	def _create_layout_page_exif(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._create_label(panel, _("Exif")))
		listctrl = self._listctrl_exif = wx.ListCtrl(panel, -1,
				style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		sizer.Add(listctrl, 1, wx.EXPAND | wx.LEFT | wx.TOP, 12)
		listctrl.InsertColumn(0, _('Tag'))
		listctrl.InsertColumn(1, _('Value'))
		panel_sizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)
		exif = self._item.exif_data
		if exif is not None:
			for key, val in sorted(exif.iteritems()):
				key_human, val_human = eimage.get_tag_human(key, val)
				idx = listctrl.InsertStringItem(sys.maxint, str(key_human))
				listctrl.SetStringItem(idx, 1, unicode(val_human,
						errors='replace'))
			listctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
			listctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
		return panel

	def _create_layout_page_tags(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._create_label(panel, _("Tags")))
		self._tags_listbox = TagsListBox(panel, -1)
		item_tags = self._item.tags
		if not self.readonly:
			all_tags = self._item.collection.tags_provider.tags
		else:
			all_tags = item_tags
		self._tags_listbox.show(all_tags, item_tags)
		sizer.Add(self._tags_listbox, 1, wx.EXPAND | wx.ALL, 12)
		panel_sizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)
		return panel

	def _create_layout_page_other(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self._create_label(panel, _("Shot date")))
		subsizer = wx.BoxSizer(wx.VERTICAL)
		shot_date_present = (self._item.shot_date is not None
				and self._item.shot_date > 0)
		if not self.readonly:
			self._cb_shot_date = wx.CheckBox(panel, 1, _("Set shot date"))
			self._cb_shot_date.SetValue(shot_date_present)
			self.Bind(wx.EVT_CHECKBOX, self._on_checkbox_short_date,
					self._cb_shot_date)
			subsizer.Add(self._cb_shot_date)
		date_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self._lb_shot_date = wx.StaticText(panel, 1, _("Shot date:"))
		self._lb_shot_date.Enable(not self.readonly and shot_date_present)
		date_sizer.Add(self._lb_shot_date, 1, wx.EXPAND | wx.ALL, 5)
		date_sizer.Add((5, 5))
		self._dp_shot_date = wx.DatePickerCtrl(panel, size=(120, -1),
				style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY | wx.SUNKEN_BORDER)
		self._dp_shot_date.Enable(not self.readonly and shot_date_present)
		date_sizer.Add(self._dp_shot_date, 0, wx.EXPAND, wx.EXPAND | wx.ALL, 5)
		date_sizer.Add((5, 5))
		self._tc_shot_time = masked.TimeCtrl(panel, -1, fmt24hr=True)
		self._tc_shot_time.SetEditable(not self.readonly and shot_date_present)
		self._tc_shot_time.Enable(not self.readonly and shot_date_present)
		date_sizer.Add(self._tc_shot_time, 0, wx.EXPAND, wx.EXPAND | wx.ALL, 5)
		if shot_date_present:
			date = wx.DateTime()
			date.SetTimeT(self._item.shot_date)
			self._dp_shot_date.SetValue(date)
			self._tc_shot_time.SetValue(date)
		subsizer.Add(date_sizer)
		sizer.Add(subsizer, 0, wx.EXPAND | wx.ALL, 12)
		panel_sizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)
		return panel

	def _create_layout_page_map(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)
		self._panel_map = PanelOsmMap(panel)
		panel_sizer.Add(self._panel_map, 1, wx.EXPAND | wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)
		pos = self._item.geo_position
		appconfig = AppConfig()
		if pos:
			lat, lon = pos
			zoom = 10
			self._panel_map.add_waypoints((lon, lat, self._item.name or _('Image')))
		else:
			lon = appconfig.get('last_map', 'lon', 0.0)
			lat = appconfig.get('last_map', 'lat', 0.0)
			zoom = appconfig.get('last_map', 'zoom', 4)
		self._panel_map.show_map((lon, lat), zoom)
		return panel

	#########################################################################

	def _on_ok(self, evt):
		pass

	def _on_close(self, evt=None):
		appconfig = AppConfig()
		appconfig.set(self._CONFIG_KEY, 'size', self.GetSizeTuple())
		appconfig.set(self._CONFIG_KEY, 'position', self.GetPositionTuple())
		if self._panel_map:
			(lon, lat), zoom = self._panel_map.center_zoom
			appconfig.set('last_map', 'lon', lon)
			appconfig.set('last_map', 'lat', lat)
			appconfig.set('last_map', 'zoom', zoom)
		if evt is not None:
			evt.Skip()

	def _on_checkbox_short_date(self, evt):
		value = evt.IsChecked()
		self._dp_shot_date.Enable(value)
		self._tc_shot_time.Enable(value)
		self._lb_shot_date.Enable(value)

	def _on_btn_next(self, evt):
		self._on_close()
		self.EndModal(wx.ID_FORWARD)

	def _on_btn_prev(self, evt):
		self._on_close()
		self.EndModal(wx.ID_BACKWARD)


# vim: encoding=utf8:
