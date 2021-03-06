#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
MainWndView

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski, 2004-2010'
__revision__ = '$Id$'

__all__ = ['WndMainView']


import os.path
import logging

import wx

from photocat import version
from photocat.lib.appconfig import AppConfig
from photocat.lib.wxtools import iconprovider
from photocat.lib.wxtools.guitools import create_menu, create_toolbar_button, \
	create_menu_item
from photocat.gui.components.dirstree import DirsTree
from photocat.gui.components.infopanel import InfoPanel
from photocat.gui.components.thumbctrl import ThumbCtrl

_LOG = logging.getLogger(__name__)
_DEFAULT_ADD_OPTIONS = {
		'filter_folder_names': None,
		'include_empty': 0}


class WndMainView(wx.Frame):		# pylint: disable-msg=R0902
	""" MainWnd """

	def __init__(self, app, debug):
		_LOG.debug('MainWnd.__init__')

		appconfig = AppConfig()
		size = appconfig.get('main_wnd', 'size', (800, 600))

		wx.Frame.__init__(self, None, -1, version.NAME, size=size)

		self._debug = debug
		self._app = app
		self._layout_splitter = None
		self._info_panel_size = None
		self._last_used_dir = os.path.expanduser('~')
		self._menu_view_show_captions = None
		self._layout_splitter_h = None
		self._layout_splitter_v = None
		self._toolbar = None
		self._photo_list = None
		self._menu_view_group_date = None
		self._dirs_tree = None
		self._menu_view_sort_name = None
		self._main_menu_file_recent_item = None
		self._menu_view_show_info = None
		self._main_menu_file = None
		self._main_menu_file_recent = None
		self._menu_bar = None
		self._menu_view_group_path = None
		self._menu_view_sort_date = None
		self._tb_save = None
		self._menu_view_sort_desc = None
		self._tb_add_disk = None
		self._info_panel = None
		self._menu_view_show_recur = None
		self._main_menu_collection = None
		self._tb_find = None

		self.SetIcon(iconprovider.get_icon('icon'))

		self.SetMenuBar(self._create_main_menu())
		self._create_toolbar()
		self._create_layout(appconfig)
		self.CreateStatusBar(2, wx.ST_SIZEGRIP)
		self.SetStatusWidths([-1, 50])

		self._print_data = wx.PrintData()

		position = appconfig.get('main_wnd', 'position')
		if position is None:
			self.Centre(wx.BOTH)
		else:
			self.Move(position)

	############################################################################

	def _create_layout(self, appconfig):
		splitter = self._layout_splitter_v = wx.SplitterWindow(self, -1,
				style=wx.SW_BORDER)
		splitter2 = self._layout_splitter_h = wx.SplitterWindow(splitter, -1,
				style=wx.SW_BORDER)
		splitter2.SplitHorizontally(self._create_layout_photolist(splitter2),
				self._create_layout_info(splitter2))
		splitter2.SetMinimumPaneSize(0)
		splitter.SplitVertically(self._create_layout_tree(splitter), splitter2)
		splitter.SetSashGravity(0.0)
		splitter2.SetSashGravity(1.0)
		splitter.SetSashPosition(appconfig.get('main_wnd', 'splitter_v', 200))
		splitter2.SetSashPosition(appconfig.get('main_wnd', 'splitter_h', -1))

	def _create_main_menu(self):
		self._menu_bar = menu_bar = wx.MenuBar()
		menu_bar.Append(self._create_main_menu_file(), _('&File'))
		menu_bar.Append(self._create_main_menu_edit(), _('&Edit'))
		menu_bar.Append(self._create_main_menu_view(), _('&View'))
		menu_bar.Append(self._create_main_menu_help(), _('Help'))
		if self._debug:
			menu_bar.Append(self._create_main_menu_debug(), '&Debug')

		return menu_bar

	def _create_main_menu_file(self):
		self._main_menu_file = create_menu(self, (
			(_('&New'), 'Ctrl-N', _('Create new collection'), self._on_file_new,
					wx.ID_NEW, wx.ART_NEW),
			(_('&Open'), 'Ctrl+O', _('Open collection'), self._on_file_open,
					wx.ID_OPEN, wx.ART_FILE_OPEN),
			('-'),
			(_('&Save'), 'Ctrl+S', _('Save the current collection'), self._on_file_save,
					wx.ID_SAVE, wx.ART_FILE_SAVE),
			(_('&Rebuild collection'), None, _('Rebuild collection'),
					self._on_file_rebuild),
			('-'),
			(_('&Export to PDF...'), None, '', self._on_file_export_pdf),
			(_('&Print'), 'Ctrl+P', '', self._on_file_print_prv, wx.ID_PRINT,
					wx.ART_PRINT),
			('-'),
			(_('Properties'), 'Alt+Return',
					_('Show informations about selected calalog...'),
					self._on_collection_info),
			('-'),
			('-'),
			(_('&Close'), 'Ctrl+W', _('Close the current collection'),
					self._on_file_close),
			(_('&Quit'), 'Ctrl+Q', _('Quit the application'), self._on_menu_close,
					wx.ID_EXIT, wx.ART_QUIT)))

		self._main_menu_file_recent = wx.Menu()
		self._main_menu_file_recent_item = self._main_menu_file.InsertMenu(11,
				-1, _('Recent files'), self._main_menu_file_recent)

		return self._main_menu_file

	def _create_main_menu_edit(self):
		menu = create_menu(self, (
			(_('&Add Disk...'), None, _('Add disk to collection'),
					self._on_collection_add, None, wx.ART_NEW_DIR),
			(_('&Update Disk...'), None, _('Update selected disk'),
					self._on_collection_update_disk),
			(_('&Delete Disk...'), None, _('Delete selected disk from collection'),
					self._on_collection_del_disk, None, wx.ART_DELETE),
			('-'),
			(_('Delete Selected &Dir...'), None, '', self._on_collection_del_dir),
			('-'),
			(_('&Edit Selected Files...'), None, '', self._on_collection_edit_multi),
			(_('Delete Selected &Image...'), None, '',
					self._on_collection_del_image),
			('-'),
			(_('Search...'), 'Ctrl+F', _('Search for something in calalogs'),
					self._on_collection_search, wx.ID_FIND, wx.ART_FIND),
			('-'),
			(_('Tags'), None, _('Manage collection tags...'),
					self._on_collection_edit_tags),
			(_('Pre&ferences'), None, _('Change Photo Catalog preferences'),
					self._on_file_settings, None, wx.ART_HELP_SETTINGS)))
		self._main_menu_collection = menu
		return menu

	def _create_main_menu_view(self):
		menu = wx.Menu()
		self._menu_view_show_info = create_menu_item(self, menu,
				_('[x]Show &Informations'), self._on_view_show_hide_info, accel='F4')[1]
		self._menu_view_show_captions = create_menu_item(self, menu,
				_('[x]Show &Captions'), self._on_view_show_hide_captions)[1]
		menu.AppendSeparator()
		self._menu_view_sort_name = create_menu_item(self, menu,
				_('[o]Sort by &Name '), self._on_view_sort)[1]
		self._menu_view_sort_date = create_menu_item(self, menu,
				_('[o]Sort by &Date '), self._on_view_sort)[1]
		self._menu_view_group_date = create_menu_item(self, menu,
				_('[o]&Sort and Group by Date '), self._on_view_sort)[1]
		self._menu_view_group_path = create_menu_item(self, menu,
				_('[o]Sort and Group by Pa&th '), self._on_view_sort)[1]
		menu.AppendSeparator()
		self._menu_view_sort_desc = create_menu_item(self, menu,
				_('[x]Sort Descend'), self._on_view_sort)[1]
		self._menu_view_show_recur = create_menu_item(self, menu,
				_('[x]Show All Files in Subtree'), self._on_view_sort)[1]
		return menu

	def _create_main_menu_help(self):
		menu = create_menu(self, (
			(_('&About'), None, '', self._on_help_about, wx.ID_ABOUT,
				wx.ART_INFORMATION),
		))
		return menu

	def _create_main_menu_debug(self):
		menu = create_menu(self, (
			('Shell', 'Ctrl+L', '', self._on_debug_shell, None),
			('Fill shot date', None, '', self._on_debug_fill_shot_date, None),
		))
		return menu

	def _create_toolbar(self):
		self._toolbar = toolbar = self.CreateToolBar(
				wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)
		#toolbar.SetToolBitmapSize((16, 16))

		def __cbtna(label, function, iconname, description=''):
			return create_toolbar_button(toolbar, label, function,
					imgid=iconname, description=description)

		__cbtna(_('New'), self._on_file_new, wx.ART_NEW, _('Create new collection'))
		__cbtna(_('Open'), self._on_file_open, wx.ART_FILE_OPEN,
				_('Open collection'))
		self._tb_save = __cbtna(_('Save'), self._on_file_save, wx.ART_FILE_SAVE,
				_('Save the current collection'))

		toolbar.AddSeparator()

		self._tb_find = __cbtna(_('Search'), self._on_collection_search, wx.ART_FIND,
				_('Search for something in calalogs'))

		toolbar.AddSeparator()

		self._tb_add_disk = __cbtna(_('Add disk...'), self._on_collection_add,
				wx.ART_NEW_DIR, _('Add disk to collection'))

		toolbar.AddSeparator()

		toolbar.AddControl(wx.StaticText(toolbar, -1, _('Zoom: ')))
		self._s_zoom = wx.Slider(toolbar, -1, 3, 0, 5, size=(100, -1),
				style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
		toolbar.AddControl(self._s_zoom)
		self._s_zoom_label = wx.StaticText(toolbar, -1, ' 100%')
		toolbar.AddControl(self._s_zoom_label)

		self.Bind(wx.EVT_SCROLL, self._on_zoom_scroll, self._s_zoom)

		toolbar.Realize()

	def _create_layout_tree(self, parent):
		self._dirs_tree = DirsTree(parent)
		return self._dirs_tree

	def _create_layout_photolist(self, parent):
		self._photo_list = ThumbCtrl(parent, status_wnd=self)
		return self._photo_list

	def _create_layout_info(self, parent):
		self._info_panel = InfoPanel(parent)
		return self._info_panel

	############################################################################

	def show_item(self, folder):
		''' wyświetlenia podanego folderu '''
		self._dirs_tree.show_node(folder)
		self._dirs_tree.SelectItem(folder.tree_node)

	def select_item(self, item):
		''' zaznaczenie podanego elelemntu '''
		self._photo_list.select_item(item)

	def _create_popup_menu(self, item):
		popup_menu = wx.Menu()

		def __append(name, func):
			mid = wx.NewId()
			popup_menu.Append(mid, name)
			wx.EVT_MENU(self, mid, func)

		if hasattr(item, 'subdirs'):
			__append(_('Properties'), self._on_dirtree_item_activate)

			if not item.collection.readonly:
				popup_menu.AppendSeparator()
				if item.path == '':
					__append(_('&Update disk...'), self._on_collection_update_disk)
					__append(_('&Delete disk...'), self._on_collection_del_disk)
				else:
					__append(_('Delete selected &dir...'), self._on_collection_del_dir)

			popup_menu.AppendSeparator()

		__append(_('Close collection'), self._on_file_close)
		return popup_menu

	def _create_popup_menu_image(self):
		popup_menu = wx.Menu()

		def __append(name, func):
			mid = wx.NewId()
			popup_menu.Append(mid, name)
			wx.EVT_MENU(self, mid, func)

		if self._photo_list.selected_item.disk.last_path:
			__append(_('Open'), self._on_photo_popoup_open)
			popup_menu.AppendSeparator()

		__append(_('Properties'), self._on_photo_popoup_properties)

		collection = self._photo_list.selected_item.collection
		if not collection.readonly:
			popup_menu.AppendSeparator()
			__append(_('&Delete file...'), self._on_collection_del_image)

		return popup_menu

	def _update_changed_tags(self, tags_provider, changed_tags):
		"""aktualizacja tagów w drzewie """
		if changed_tags is not None and len(changed_tags) > 0:
			for tag_item in (tags_provider[tag] for tag in changed_tags):
				if tag_item.tree_node is not None:
					self._dirs_tree.update_node_tag(tag_item)

			self._dirs_tree.update_node_tags(tags_provider)

	def _toggle_info_panel(self, show=None):
		""" przełączenie widoczności paneli informacyjnego
		@param show: None=toggle, True-wymuszenie pokazania, False=wymuszenie
		ukrycia
		"""

		if self._layout_splitter_h.IsSplit():
			if show is None or show is False:
				# panel jest pokazany - usuniecie go
				self._info_panel_size = self._layout_splitter_h.GetSashPosition()
				self._layout_splitter_h.Unsplit()
				self._info_panel.Destroy()
				self._info_panel = None
		else:
			if show is None or show is True:
				# stworzenie panelu
				self._info_panel = self._create_layout_info(self._layout_splitter_h)
				wind1 = self._layout_splitter_h.GetWindow1()
				self._layout_splitter_h.SplitHorizontally(wind1, self._info_panel,
						self._info_panel_size)

				# odswierzenie danych w panelu
				self._on_thumb_sel_changed(None)
				item = self._dirs_tree.selected_item
				if item is not None and hasattr(item, 'subdirs'):
						#isinstance(item, Directory):
					self._info_panel.show_folder(item)

	def _update_tags_timeline(self, collection):
		'''odświerzenie dir tree:
		tags, timeline '''
		self._dirs_tree.update_node_tags(collection.tags_provider, True)
		self._dirs_tree.update_timeline_node(collection.timeline)

	def _info_panel_clear(self):
		''' wyczyszczenie info-panelu '''
		if self._info_panel is not None:
			self._info_panel.clear()

	###

	def _on_file_new(self, evt):
		raise NotImplementedError()

	def _on_file_open(self, evt):
		raise NotImplementedError()

	def _on_file_save(self, evt):
		raise NotImplementedError()

	def _on_file_close(self, evt):
		raise NotImplementedError()

	def _on_file_rebuild(self, evt):
		raise NotImplementedError()

	def _on_file_print_prv(self, evt):
		raise NotImplementedError()

	def _on_file_export_pdf(self, evt):
		raise NotImplementedError()

	def _on_file_settings(self, evt):
		raise NotImplementedError()

	def _on_menu_close(self, evt):
		raise NotImplementedError()

	def _on_collection_add(self, evt):
		raise NotImplementedError()

	def _on_collection_update_disk(self, evt):
		raise NotImplementedError()

	def _on_collection_del_disk(self, evt):
		raise NotImplementedError()

	def _on_collection_del_dir(self, evt):
		raise NotImplementedError()

	def _on_collection_del_image(self, evt):
		raise NotImplementedError()

	def _on_collection_edit_multi(self, evt):
		raise NotImplementedError()

	def _on_collection_search(self, evt):
		raise NotImplementedError()

	def _on_collection_info(self, evt):
		raise NotImplementedError()

	def _on_collection_edit_tags(self, evt):
		raise NotImplementedError()

	def _on_view_show_hide_info(self, evt):
		raise NotImplementedError()

	def _on_view_show_hide_captions(self, evt):
		raise NotImplementedError()

	def _on_view_sort(self, evt):
		raise NotImplementedError()

	def _on_help_about(self, evt):
		raise NotImplementedError()

	def _on_debug_shell(self, evt):
		raise NotImplementedError()

	def _on_debug_fill_shot_date(self, evt):
		raise NotImplementedError()

	def _on_photo_popoup_properties(self, evt):
		raise NotImplementedError()

	def _on_photo_popoup_open(self, evt):
		raise NotImplementedError()

	def _on_thumb_sel_changed(self, evt):
		raise NotImplementedError()

	def _on_dirtree_item_activate(self, evt):
		raise NotImplementedError()

	def _on_zoom_scroll(self, evt):
		raise NotImplementedError()

# vim: encoding=utf8: ff=unix:
