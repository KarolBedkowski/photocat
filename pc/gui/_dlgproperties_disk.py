#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
 Photo Catalog v 1.x  (pc)
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

__all__			= ['DlgPropertiesDisk']


import wx

from kpylibs.dialogs	import message_box_error

from _dlg_properties_base	import DlgPropertiesBase

_ = wx.GetTranslation



class DlgPropertiesDisk(DlgPropertiesBase):
	''' Dialog własności dysku '''
	
	_CONFIG_KEY='properties_disk_wnd'

	def __init__(self, parent, item):
		DlgPropertiesBase.__init__(self, parent, item)


	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_layout_page_main(notebook),	_('Main'))
		notebook.AddPage(self._create_layout_page_desc(notebook),	_('Comment'))
		notebook.AddPage(self._create_layout_page_tags(notebook),	_('Tags'))
		return notebook


	def _create_layout_page_main(self, parent):
		panel = wx.Panel(parent, -1)
		sizer = wx.BoxSizer(wx.VERTICAL)

		bsizer = wx.FlexGridSizer(2, 2, 5, 12)
		bsizer.AddGrowableCol(1)

		bsizer.Add(self._create_label(panel, _("Name") + ":"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		self._tc_name = wx.TextCtrl(panel, -1)
		bsizer.Add(self._tc_name , 1, wx.EXPAND)

		key_name = _("Name")
		for dummy, key, val in sorted(self._item.info):
			if key == key_name:
				self._tc_name.SetValue(val)

			elif key == '':
				bsizer.Add((1,5))
				bsizer.Add((1,5))

			else:
				bsizer.Add(self._create_label(panel, key + ":"), 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
				bsizer.Add(wx.StaticText(panel, -1, str(val)), 1, wx.EXPAND)

		sizer.Add(bsizer, 1, wx.ALL|wx.ALIGN_CENTER, 12)
		panel.SetSizerAndFit(sizer)
		return panel


	#########################################################################


	def _on_ok(self, evt):
		item		= self._item
		changed		= False

		new_name = self._tc_name.GetValue()
		if len(new_name.strip()) == 0:
			message_box_error(self, _("You must provide name for disk"), _("Disk"))
			self._tc_name.SetFocus()
			return

		if new_name != item.name:
			changed = True
			item.name = new_name

		new_desc		= self._textctrl_desc.GetValue().strip()
		changed_desc	= (new_desc != '') if (item.desc is None) else (new_desc != item.desc)

		if changed_desc:
			item.desc	= new_desc
			changed		= True

		new_tags = self._tags_listbox.selected
		item_tags = item.tags
		changed_tags = sorted(item_tags or []) != sorted(new_tags or [])

		if changed_tags:
			self.changed_tags	= item.set_tags(new_tags)
			changed				= True

		self._on_close()

		if changed:
			self.EndModal(wx.ID_OK)

		else:
			self.EndModal(wx.ID_CANCEL)




# vim: encoding=utf8:
