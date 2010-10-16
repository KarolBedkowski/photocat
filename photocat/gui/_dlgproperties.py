#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.x (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__revision__ = '$Id$'

__all__ = ['DlgProperties']


import wx

from photocat.engine import image
from photocat.gui._dlg_properties_base import DlgPropertiesBase
from photocat.lib.appconfig import AppConfig


class DlgProperties(DlgPropertiesBase):
	''' Dialog o programie '''

	def __init__(self, parent, item, show_next_prev=False):
		DlgPropertiesBase.__init__(self, parent, item, item.collection.readonly,
				show_next_prev=show_next_prev)

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

		self._bmp_preview = wx.StaticBitmap(panel, -1)

		appconfig = AppConfig()
		thumbw = appconfig.get('settings', 'thumb_width', 200)
		thumbh = appconfig.get('settings', 'thumb_height', 200)

		self._bmp_preview.SetBitmap(image.load_bitmap_from_item_with_size(
				self._item, thumbw, thumbh, 1)[0])
		sizer.Add(self._bmp_preview, 0, wx.ALIGN_CENTER | wx.ALL, 12)

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

	#########################################################################

	def _on_ok(self, evt):
		item = self._item
		changed = False

		new_desc = self._textctrl_desc.GetValue().strip()
		changed_desc = ((new_desc != '')
				if (item.desc is None) else (new_desc != item.desc))

		if changed_desc:
			item.desc = new_desc
			changed = True

		new_tags = self._tags_listbox.selected
		item_tags = item.tags
		changed_tags = sorted(item_tags or []) != sorted(new_tags or [])

		if changed_tags:
			self.changed_tags = item.set_tags(new_tags)
			changed = True

		if self._cb_shot_date.IsChecked():
			sdate = self._dp_shot_date.GetValue()
			stime = self._tc_shot_time.GetValue(as_wxDateTime=True)

			sdate.SetHour(stime.GetHour())
			sdate.SetMinute(stime.GetMinute())
			sdate.SetSecond(stime.GetSecond())

			sdate_val = sdate.GetTicks()
			if item.shot_date is None or item.shot_date != sdate_val:
				item.shot_date = sdate_val
				changed = True
		elif item.shot_date is not None:
			item.shot_date = None
			changed = True

		if self.changed_geotag is not None:
			item.geo_position = self.changed_geotag
			changed = True

		self._on_close()

		if changed:
			self.EndModal(wx.ID_OK)
		else:
			self.EndModal(wx.ID_CANCEL)




# vim: fileencoding=utf8: ff=unix:
