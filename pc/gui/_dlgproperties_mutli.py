#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
 Photo Catalog v 1.x (pc)
 Copyright (c) Karol Będkowski, 2004-2009

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

__all__			= ['DlgPropertiesMulti']


import wx
from wx.lib import masked

from components.tags_list_box import TagsListBox

from pc.gui._dlg_properties_base	import DlgPropertiesBase

_ = wx.GetTranslation



class DlgPropertiesMulti(DlgPropertiesBase):
	''' Dialog o programie '''
	
	_CONFIG_KEY = 'properties_multi_wnd'

	def __init__(self, parent, item, result):
		DlgPropertiesBase.__init__(self, parent, item)
		self._result = result


	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_layout_page_desc(notebook),	_('Comment'))
		notebook.AddPage(self._create_layout_page_tags(notebook),	_('Tags'))
		notebook.AddPage(self._create_layout_page_other(notebook),	_('Other'))
		return notebook


	def _create_layout_page_desc(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(self._create_label(panel, _("Comment")))

		self._cb_comment = wx.CheckBox(panel, -1, _("Set comment"))
		sizer.Add(self._cb_comment, 0, wx.LEFT|wx.TOP, 12)
		self.Bind(wx.EVT_CHECKBOX, self._on_checkbox_set_comment, 
				self._cb_comment)

		textctrl = self._textctrl_desc = wx.TextCtrl(panel, -1, 
				style=wx.TE_MULTILINE)
		textctrl.Enable(False)
		textctrl.SetValue(str(self._item.desc or ''))

		sizer.Add(textctrl, 1, wx.EXPAND|wx.LEFT|wx.TOP, 12)

		panel_sizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)

		return panel


	def _create_layout_page_tags(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(self._create_label(panel, _("Tags")))

		self._cb_tags = wx.CheckBox(panel, -1, _("Set tags"))
		sizer.Add(self._cb_tags, 0, wx.LEFT|wx.TOP, 12)
		self.Bind(wx.EVT_CHECKBOX, self._on_checkbox_set_tags, self._cb_tags)

		self._tags_listbox = TagsListBox(panel, -1)
		self._tags_listbox.Enable(False)
		item_tags = self._item.tags
		all_tags = self._item.catalog.tags_provider.tags
		self._tags_listbox.show(all_tags, item_tags)

		sizer.Add(self._tags_listbox, 1, wx.EXPAND|wx.ALL, 12)

		panel_sizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)
		return panel


	def _create_layout_page_other(self, parent):
		panel = wx.Panel(parent, -1)
		panel_sizer = wx.BoxSizer(wx.VERTICAL)

		sizer = wx.BoxSizer(wx.VERTICAL)

		sizer.Add(self._create_label(panel, _("Shot date")))

		subsizer = wx.BoxSizer(wx.VERTICAL)

		self._cb_shot_date = wx.CheckBox(panel, 1, _("Set shot date"),
				style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
		self._cb_shot_date.Set3StateValue(wx.CHK_UNDETERMINED )
		self.Bind(wx.EVT_CHECKBOX, self._on_checkbox_short_date, 
				self._cb_shot_date)
		subsizer.Add(self._cb_shot_date)

		date_sizer = wx.BoxSizer(wx.HORIZONTAL)

		self._lb_shot_date = wx.StaticText(panel, 1, _("Shot date:"))
		self._lb_shot_date.Enable(False)
		date_sizer.Add(self._lb_shot_date , 1, wx.EXPAND|wx.ALL, 5)

		date_sizer.Add((5, 5))

		self._dp_shot_date = wx.DatePickerCtrl(panel , size=(120, -1),
				style=wx.DP_DROPDOWN|wx.DP_SHOWCENTURY|wx.SUNKEN_BORDER)
		self._dp_shot_date.Enable(False)
		date_sizer.Add(self._dp_shot_date, 0, wx.EXPAND, wx.EXPAND|wx.ALL, 5)

		date_sizer.Add((5, 5))

		self._tc_shot_time = masked.TimeCtrl(panel , -1, fmt24hr=True)
		self._tc_shot_time.Enable(False)
		date_sizer.Add(self._tc_shot_time, 0, wx.EXPAND, wx.EXPAND|wx.ALL, 5)

		if self._item.shot_date is not None:
			date = wx.DateTime()
			date.SetTimeT(self._item.shot_date)
			self._dp_shot_date.SetValue(date)
			self._tc_shot_time.SetValue(date)

		subsizer.Add(date_sizer)
		sizer.Add(subsizer, 0, wx.EXPAND|wx.ALL, 12)
		panel_sizer.Add(sizer, 1, wx.EXPAND|wx.ALL, 12)
		panel.SetSizerAndFit(panel_sizer)

		return panel



	#########################################################################


	def _on_ok(self, evt):
		item		= self._item
		result		= self._result

		if self._cb_comment.IsChecked():
			new_desc		= self._textctrl_desc.GetValue().strip()
			changed_desc	= ((new_desc != '') 
					if (item.desc is None) else (new_desc != item.desc))

			if changed_desc:
				result['desc'] = new_desc

		if self._cb_tags.IsChecked():
			new_tags = self._tags_listbox.selected
			item_tags = item.tags
			changed_tags = sorted(item_tags or []) != sorted(new_tags or [])

			if changed_tags:
				result['tags'] = new_tags

		if self._cb_shot_date.Get3StateValue() == wx.CHK_CHECKED:
			sdate = self._dp_shot_date.GetValue()
			stime = self._tc_shot_time.GetValue(as_wxDateTime=True)

			sdate.SetHour(stime.GetHour())
			sdate.SetMinute(stime.GetMinute())
			sdate.SetSecond(stime.GetSecond())

			sdate_val = sdate.GetTicks()
			result['shot_date'] = sdate_val

		elif self._cb_shot_date.Get3StateValue() == wx.CHK_UNCHECKED:
			result['shot_date'] = None

		self._on_close()

		if len(result) > 0:
			self.EndModal(wx.ID_OK)

		else:
			self.EndModal(wx.ID_CANCEL)


	def _on_checkbox_short_date(self, evt):
		value = self._cb_shot_date.Get3StateValue() == wx.CHK_CHECKED
		self._dp_shot_date.Enable(value)
		self._tc_shot_time.Enable(value)
		self._lb_shot_date.Enable(value)


	def _on_checkbox_set_comment(self, evt):
		self._textctrl_desc.Enable(evt.IsChecked())


	def _on_checkbox_set_tags(self, evt):
		self._tags_listbox.Enable(evt.IsChecked())


# vim: encoding=utf8:
