#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.x  (photocat)
Copyright (c) Karol Będkowski, 2004-2009

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'

__all__ = ['DlgPropertiesDir']


import wx

from photocat.gui._dlg_properties_base import DlgPropertiesBase


class DlgPropertiesDir(DlgPropertiesBase):
	''' Dialog o programie '''

	_CONFIG_KEY = 'properties_dir_wnd'

	def __init__(self, parent, item):
		readonly = item.collection.readonly

		DlgPropertiesBase.__init__(self, parent, item, readonly)

	def _create_layout_notebook(self):
		notebook = self._notebook = wx.Notebook(self, -1)
		notebook.AddPage(self._create_layout_page_main(notebook), _('Main'))
		notebook.AddPage(self._create_layout_page_desc(notebook), _('Comment'))
		notebook.AddPage(self._create_layout_page_tags(notebook), _('Tags'))
		return notebook

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

		self._on_close()

		if changed:
			self.EndModal(wx.ID_OK)

		else:
			self.EndModal(wx.ID_CANCEL)


# vim: encoding=utf8:
