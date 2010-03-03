#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
MainWnd

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'

__all__ = ['WndMain']


import os.path
import logging

import wx

from photocat.model import Catalog, Directory, Disk, FileImage, Tag, Timeline
from photocat.storage.storage import Storage
from photocat.engine import ecatalog, eprint, epdf
from photocat.lib.appconfig import AppConfig
from photocat.lib.wxtools import dialogs
from photocat.lib.wxtools.wnd_shell import WndShell
from photocat.gui._dlgabout import show_about_box
from photocat.gui._dlgproperties import DlgProperties
from photocat.gui._dlgproperties_dir import DlgPropertiesDir
from photocat.gui._dlgproperties_disk import DlgPropertiesDisk
from photocat.gui._dlgproperties_mutli import DlgPropertiesMulti
from photocat.gui._dlgsearch import DlgSearchProvider
from photocat.gui._dlgsettings import DlgSettings
from photocat.gui._dlg_edit_tags import show_dlg_edit_tags
from photocat.gui.components.thumbctrl import EVT_THUMB_DBCLICK, \
		EVT_THUMB_SELECTION_CHANGE

from .wndmain_view import WndMainView

_LOG = logging.getLogger(__name__)
_DEFAULT_ADD_OPTIONS = {
		'filter_folder_names': None,
		'include_empty': 0}


class WndMain(WndMainView):
	""" MainWnd """

	def __init__(self, app, debug):
		WndMainView.__init__(self, app, debug)
		_LOG.debug('MainWnd.__init__')

		self._catalogs = []
		self._info_panel_size = None
		self._last_used_dir = os.path.expanduser('~')
		self._current_show_images = []

		self._update_last_open_files()
		self._update_menus_toolbars()
		self._update_settings()

		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Bind(wx.EVT_SIZE, self._on_size)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_dirtree_item_select,
				self._dirs_tree)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_dirtree_item_activate,
				self._dirs_tree)
		self._photo_list.Bind(EVT_THUMB_SELECTION_CHANGE,
				self._on_thumb_sel_changed)
		self._photo_list.Bind(EVT_THUMB_DBCLICK, self._on_thumb_dclick)
		self.Bind(wx.EVT_MENU_RANGE, self._on_file_history, id=wx.ID_FILE1,
				id2=wx.ID_FILE9)
		self.Bind(wx.EVT_TREE_ITEM_MENU, self._on_dirtree_context_menu,
				self._dirs_tree)
		self._dirs_tree.Bind(wx.EVT_RIGHT_DOWN, self._on_dirtree_right_down,
				self._dirs_tree)
		self._dirs_tree.Bind(wx.EVT_KEY_DOWN, self._on_dirtree_key_down)
		self._photo_list.Bind(wx.EVT_CHAR, self._on_photolist_key_down)
		self._photo_list.Bind(wx.EVT_RIGHT_UP, self._on_photolist_popupmenu)

	############################################################################

	@property
	def catalogs_not_loaded(self):
		''' Check is no catalog loaded '''
		return not self._catalogs

	@property
	def selected_catalog(self):
		''' get selected or first catalog '''
		if self.catalogs_not_loaded:
			return None

		tree_selected = self._dirs_tree.selected_item
		catalog = (self._catalogs[0] if tree_selected is None
				else tree_selected.catalog)

		return catalog

	############################################################################

	def _on_menu_close(self, evt):
		'''_on_menu_close'''
		self.Close()

	def _on_close(self, evt):
		'''_on_close'''
		dirty_catalogs = [catalog for catalog in self._catalogs if catalog.dirty]

		if len(dirty_catalogs) > 0:
			for catalog in dirty_catalogs:
				res = dialogs.message_box_warning_yesnocancel(self,
						_("Catalog %s was changed.\nSave it?") % catalog.caption,
						_('Catalog'))
				if res == wx.ID_CANCEL:
					return
				elif res == wx.ID_YES:
					self._save_catalog(catalog)

		elif not dialogs.message_box_question_yesno(self, _('Close program?'),
				_('Exit')):
			return

		for catalog in self._catalogs:
			ecatalog.catalog_close(catalog)

		del self._catalogs
		self._catalogs = None

		self._photo_list.clear_cache()

		appconfig = AppConfig()
		appconfig.set('main_wnd', 'size', self.GetSizeTuple())
		appconfig.set('main_wnd', 'position', self.GetPositionTuple())
		appconfig.set('main_wnd', 'splitter_h',
				self._layout_splitter_h.GetSashPosition())
		appconfig.set('main_wnd', 'splitter_v',
				self._layout_splitter_v.GetSashPosition())

		self._app.ExitMainLoop()
		evt.Skip()

	def _on_size(self, evt):
		'''_on_size'''
		self._dirs_tree.Refresh()
		evt.Skip()

	def _on_file_new(self, evt):
		'''_on_file_new '''
		filename = dialogs.dialog_file_save(self, _('Catalog file name'),
				'*.index', default_dir=self._last_used_dir)
		if filename is not None:
			if not filename.endswith('.index'):
				filename = filename + '.index'

			if ecatalog.check_new_file_exists(filename)[0]:
				if not dialogs.message_box_question_yesno(self,
						_('File exists!\nOverwrite?'), _('Error')):
					return

			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				catalog = ecatalog.new_catalog(filename)
				self._catalogs.append(catalog)
				self._dirs_tree.add_catalog(catalog)
			except StandardError, err:
				_LOG.exception('WndMain._on_file_new(%s)', filename)
				dialogs.message_box_error(self,
						(_('Error opening file %s:\n') % filename) + err.message,
						_('New file'))
				self.SetStatusText(_('Error: %s') % err.message)
			else:
				self._update_last_open_files(filename)
				self._update_menus_toolbars()
				self._last_used_dir = os.path.dirname(filename)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)

	def _on_file_open(self, evt):
		''' _on_file_open '''
		filename = dialogs.dialog_file_load(self, _('Open file'), '*.index',
				default_dir=self._last_used_dir)
		if filename is not None:
			if not filename.endswith('.index'):
				filename = filename + '.index'

			self.open_file(filename)
			self._update_menus_toolbars()
			self._last_used_dir = os.path.dirname(filename)

	def _on_file_save(self, evt):
		'''_on_file_save '''
		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			for cat in self._catalogs:
				self._save_catalog(cat)
				self._dirs_tree.update_catalog_node(cat)
		else:
			self._save_catalog(tree_selected.catalog)
			self._dirs_tree.update_catalog_node(tree_selected.catalog)

	def _on_file_close(self, evt):
		''' _on_file_close '''
		catalog = self.selected_catalog
		if catalog is None:
			return

		if catalog.dirty:
			res = dialogs.message_box_warning_yesnocancel(self,
					_('Catalog %s has unsaved changes!\nSave before close??') \
					% catalog.caption,
					_('Catalog'))

			if res == wx.ID_YES:
				self._save_catalog(catalog)
			elif res == wx.ID_CANCEL:
				return

		elif not dialogs.message_box_question_yesno(self,
				_('Close catalog %s?') % catalog.caption, _('Close')):
			return

		self._dirs_tree.delete_item(catalog)
		ecatalog.catalog_close(catalog)
		idx = [idx for idx, cat in enumerate(self._catalogs)
				if cat.name == catalog.name]
		del self._catalogs[idx[0]]
		self._update_menus_toolbars()
		DlgSearchProvider().close_all()
		self._photo_list.clear_cache()

	def _on_file_rebuild(self, evt):
		''' _on_file_rebuild '''
		catalog = self.selected_catalog
		if catalog is None:
			return

		if not dialogs.message_box_question_yesno(self,
				_('Rebuild catalog %s?') % catalog.caption, 'photocat'):
			return

		if ecatalog.rebuild(catalog, self):
			self._save_catalog(catalog)

	def _on_file_settings(self, evt):
		''' _on_file_settings '''
		dlg = DlgSettings(self)
		if dlg.ShowModal() == wx.ID_OK:
			self._update_settings()
		dlg.Destroy()

	def _on_file_export_pdf(self, evt):
		''' _on_file_export_pdf '''
		if len(self._current_show_images) > 0 and epdf.EPDF_AVAILABLE:
			sort_key_func, reverse = self._get_sort_function(True, True)
			images = sorted(self._current_show_images, key=sort_key_func,
					reverse=reverse)
			options = {
					'show_captions': self._photo_list.show_captions,
					'group_by': self._photo_list.group_by}
			epdf.create_pdf(self, images, options)

	def _on_file_print_prv(self, evt):
		''' _on_file_print_prv '''
		if len(self._current_show_images) > 0:
			sort_key_func, reverse = self._get_sort_function(True, True)
			images = sorted(self._current_show_images, key=sort_key_func,
					reverse=reverse)

			appconfig = AppConfig()
			options = {
				'fontdata': dict(appconfig.get_items('settings') or []),
				'thumb_width': self._photo_list.thumb_width,
				'thumb_height': self._photo_list.thumb_height,
				'show_captions': self._photo_list.show_captions,
				'group_by': self._photo_list.group_by}
			eprint.print_preview(self, self._print_data, images, options)

	def _on_view_show_hide_info(self, evt):
		""" wybór z menu widok->pokaż/ukryj info """
		AppConfig().set('settings', 'view_show_info',
				self._menu_view_show_info.IsChecked())
		self._toggle_info_panel()

	def _on_view_show_hide_captions(self, evt):
		""" wybór z menu widok->pokaż/ukryj podpisy """
		show_captions = self._menu_view_show_captions.IsChecked()
		AppConfig().set('settings', 'view_show_captions', show_captions)
		self._photo_list.show_captions = show_captions
		self._photo_list.update()
		self._photo_list.Refresh()

	def _on_view_sort(self, evt):
		if self._menu_view_show_recur.IsChecked():
			self._on_dirtree_item_select(evt)
		else:
			self._show_dir(None)

	def _on_help_about(self, evt):
		show_about_box(self)

	def _on_debug_shell(self, evt):
		WndShell(self, locals()).Show()

	def _on_debug_fill_shot_date(self, evt):
		catalog = self.selected_catalog
		if catalog is not None:
			catalog.fill_shot_date()

	def _on_catalog_add(self, evt):
		catalog = self.selected_catalog
		if catalog is not None:
			disk = None
			try:
				disk = ecatalog.add_disk_to_catalog(catalog, self)
			except StandardError:
				_LOG.exception('WndMain._on_catalog_add()')

			else:
				if disk is not None:
					#self._save_catalog(catalog, True)
					self._dirs_tree.update_node_disk(disk)
					self._update_tags_timeline(catalog)
					self._dirs_tree.update_catalog_node(catalog)

			self._update_menus_toolbars()

	def _on_catalog_update_disk(self, evt):
		if self.catalogs_not_loaded:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			return

		disk = tree_selected.disk
		try:
			ecatalog.update_disk_in_catalog(disk.catalog, disk, self)
		except StandardError:
			_LOG.exception('WndMain._on_catalog_update_disk()')

		else:
			if disk is not None:
				catalog = disk.catalog
				#self._save_catalog(catalog, True)
				self._dirs_tree.update_node_disk(disk)
				self._update_tags_timeline(catalog)
				self._dirs_tree.update_catalog_node(catalog)

			self._update_menus_toolbars()

	def _on_catalog_del_disk(self, evt):
		if self.catalogs_not_loaded:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Disk):
			dialogs.message_box_error(self, _('No disk selected'),
					_('Delete disk'))
			return

		if dialogs.message_box_warning_yesno(self,
				_('Delete disk %s?') % tree_selected.name, 'photocat'):
			self._dirs_tree.delete_item(tree_selected)
			catalog = tree_selected.catalog
			catalog.remove_disk(tree_selected)
			self._dirs_tree.update_catalog_node(catalog)
			self._update_tags_timeline(tree_selected.catalog)
			self._update_menus_toolbars()

	def _on_catalog_del_dir(self, evt):
		if self.catalogs_not_loaded:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			dialogs.message_box_error(self, _('No directory selected'),
					_('Delete directory'))
			return

		if dialogs.message_box_warning_yesno(self,
				_('Delete directory %s?') % tree_selected.name, _('Delete directory')):
			self._dirs_tree.delete_item(tree_selected)
			tree_selected.parent.remove_subdir(tree_selected)
			self._update_tags_timeline(tree_selected.catalog)
			self._update_menus_toolbars()

	def _on_catalog_del_image(self, evt):
		''' _on_catalog_del_image '''
		if self.catalogs_not_loaded:
			return

		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Catalog):
			return

		selected_count = self._photo_list.selected_count
		if selected_count == 0:
			return

		if dialogs.message_box_warning_yesno(self,
				_('Delete %d images?') % selected_count, _('Delete image')):
			for image in self._photo_list.selected_items:
				folder.remove_file(image)

			self._show_dir(folder)
			if self._info_panel is not None:
				self._info_panel.show_folder(folder)

			self._dirs_tree.update_catalog_node(folder.catalog)

	def _on_catalog_search(self, evt):
		''' _on_catalog_search '''
		if not self.catalogs_not_loaded:
			DlgSearchProvider().create(self, self._catalogs,
					self._dirs_tree.selected_item).Show()

	def _on_catalog_info(self, evt):
		''' _on_catalog_info '''
		if self.catalogs_not_loaded:
			return

		catalog = self.selected_catalog

		files_count, subdirs_count = 0, 0
		for disk in catalog.disks:
			(disk_files_count, disk_subdirs_count, disk_files_count2,
					disk_subdirs_count2) = disk.directory_size
			files_count += disk_files_count + disk_files_count2
			subdirs_count += disk_subdirs_count + disk_subdirs_count2

		dirty, dirtyp = catalog.dirty_objects_count

		data = dict(disks=len(catalog.disks), files=files_count,
				dirs=subdirs_count, dirty=dirty, dirtyp=dirtyp)
		info = _('Disks: %(disks)d\nDirs: %(dirs)d\nFiles: %(files)d\nDirty '
				'entries: %(dirty)d (%(dirtyp)d%%)') % data
		dialogs.message_box_info(self, info, version.NAME)

	def _on_catalog_edit_multi(self, evt):
		''' _on_catalog_edit_multi'''
		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Catalog) or len(folder.files) == 0:
			return

		image = FileImage(None, None, None, None, catalog=folder.catalog)

		result = {}

		dlg = DlgPropertiesMulti(self, image, result)
		if dlg.ShowModal() == wx.ID_OK:
			changed_tags = ecatalog.update_images_from_dict(
					self._photo_list.selected_items, result)
			folder.catalog.dirty = True
			self._dirs_tree.update_catalog_node(folder.catalog)
			self._update_changed_tags(folder.catalog.tags_provider, changed_tags)

		dlg.Destroy()

	def _on_catalog_edit_tags(self, evt):
		if self.catalogs_not_loaded:
			return

		catalog = self.selected_catalog
		if show_dlg_edit_tags(self, catalog.tags_provider):
			catalog.dirty = True
			self._dirs_tree.update_catalog_node(catalog)
			self._update_tags_timeline(catalog)

	def _on_dirtree_item_select(self, _evt):
		item = self._dirs_tree.selected_item
		show_info = True
		images_count = 0

		self.__info_panel_clear()
		self._update_menus_toolbars()

		if isinstance(item, Tag):
			item = item.files
			show_info = False
			images_count = len(item)
		elif isinstance(item, Timeline):
			# wyświtelanie timeline
			images_count = len(item.files)
			if item.level == 0:
				# nie wyświetlamy wszystkiego
				self._show_dir([])
				self._dirs_tree.Expand(self._dirs_tree.selected_node)
				return
			elif images_count > 1000:
				# jeżeli ilość plików > 1000 - ostrzeżenie i pytania
				if not dialogs.message_box_warning_yesno(self,
						_('Number of files exceed 1000!\nShow %d files?') %\
						len(item.files), version.NAME):
					self._show_dir([])
					self.SetStatusText(_('Files: %d') % len(item.files))
					self._dirs_tree.Expand(self._dirs_tree.selected_node)
					return
			show_info = False
		elif not isinstance(item, Directory):
			self._show_dir([])
			return
		else:
			images_count = len(item.files)

		self._dirs_tree.Expand(self._dirs_tree.selected_node)

		if item is not None:
			self._show_item(item, show_info, images_count)
		if self._info_panel is not None:
			if isinstance(item, Directory):
				self._info_panel.show_folder(item)
			else:
				self._info_panel.clear()

	def _on_dirtree_item_activate(self, evt):
		''' _on_dirtree_item_activate '''
		item = self._dirs_tree.selected_item
		self.__info_panel_clear()

		if isinstance(item, Catalog):
			return
		if isinstance(item, Timeline):
			if item.level == 0:
				if not self._dirs_tree.IsExpanded(item.tree_node):
					if item.dirs_count == 0:
						self._dirs_tree.update_timeline_node(item)

				self._dirs_tree.Toggle(item.tree_node)
			return

		if isinstance(item, Disk):
			dlg = DlgPropertiesDisk(self, item)
		elif isinstance(item, Directory):
			dlg = DlgPropertiesDir(self, item)
		else:
			return

		if dlg.ShowModal() == wx.ID_OK:
			item.catalog.dirty = True
			if self._info_panel is not None:
				self._info_panel.show_folder(item)

			if isinstance(item, Disk):
				self._dirs_tree.update_node_disk(item, False)
			else:
				self._dirs_tree.update_node_directory(item, False)

			self._dirs_tree.update_catalog_node(item.catalog)
			self._update_changed_tags(item.catalog.tags_provider, dlg.changed_tags)

		dlg.Destroy()

	def _on_thumb_sel_changed(self, evt):
		''' _on_thumb_sel_changed '''
		if self._info_panel is not None:
			selected = self._photo_list.selected_item
			if selected is None:
				item = self._dirs_tree.selected_item
				if isinstance(item, Directory):
					self._info_panel.show_folder(item)
				else:
					self._info_panel.clear()
			else:
				try:
					self.SetCursor(wx.HOURGLASS_CURSOR)
					self._info_panel.show(selected)
				finally:
					self.SetCursor(wx.STANDARD_CURSOR)

		self._update_menus_toolbars()

	def _on_thumb_dclick(self, _evt):
		selected_idx, items_count = self._photo_list.selected_index
		items_count -= 1
		while selected_idx > -1:
			selected = self._photo_list.get_item_by_index(selected_idx)
			show_next_prev = (selected_idx > 0, selected_idx < items_count)
			dlg = DlgProperties(self, selected, show_next_prev=show_next_prev)
			result = dlg.ShowModal()
			dlg.Destroy()
			if result == wx.ID_OK:
				if self._info_panel is not None:
					self._info_panel.show(selected)

				selected.catalog.dirty = True
				self._dirs_tree.update_catalog_node(selected.catalog)
				self._update_changed_tags(selected.catalog.tags_provider,
						dlg.changed_tags)
				break

			elif result == wx.ID_BACKWARD:
				selected_idx -= 1
			elif result == wx.ID_FORWARD:
				selected_idx += 1
			else:
				break

	def _on_file_history(self, evt):
		filehistnum = evt.GetId() - wx.ID_FILE1
		filename = AppConfig().last_open_files[filehistnum]
		self.open_file(filename)

	def _on_dirtree_context_menu(self, evt):
		tree_item = evt.GetItem()
		if tree_item is not None and tree_item.IsOk():
			item = self._dirs_tree.GetItemData(tree_item)
			if item is not None:
				data = item.GetData()
				if data is not None:
					self.PopupMenu(self._create_popup_menu(data))

	def _on_dirtree_key_down(self, evt):
		if self.catalogs_not_loaded:
			return

		if evt.GetKeyCode() == wx.WXK_DELETE:
			tree_selected = self._dirs_tree.selected_item
			if tree_selected is None:
				return

			if isinstance(tree_selected, Disk):
				self._on_catalog_del_disk(None)

			elif isinstance(tree_selected, Directory):
				self._on_catalog_del_dir(None)

	def _on_dirtree_right_down(self, evt):
		pos = evt.GetPosition()
		item, _flags = self._dirs_tree.HitTest(pos)
		if item:
			self._dirs_tree.SelectItem(item)
		evt.Skip()

	def _on_photolist_key_down(self, evt):
		if evt.m_keyCode == wx.WXK_DELETE:
			self._on_catalog_del_image(None)
		evt.Skip()

	def _on_photolist_popupmenu(self, evt):
		if self._photo_list.selected_item:
			self._photo_list.PopupMenu(self._create_popup_menu_image(),
					evt.GetPosition())

	def _on_photo_popoup_properties(self, evt):
		selected_count = self._photo_list.selected_count
		if selected_count > 1:
			self._on_catalog_edit_multi(evt)

		elif selected_count == 1:
			self._on_thumb_dclick(evt)

	############################################################################

	def open_file(self, filename):
		''' Open catalog
		@filename: full path to the index file
		'''
		if filename in (cat.catalog_filename for cat in self._catalogs):
			return

		try:
			self.SetStatusText(_('Opening %s....  Please wait...') % filename)
			self.SetCursor(wx.HOURGLASS_CURSOR)
			catalog = ecatalog.open_catalog(filename)
			self._catalogs.append(catalog)
			self._dirs_tree.add_catalog(catalog)
			self._update_last_open_files(filename)
			self.SetStatusText(filename)

		except StandardError, err:
			_LOG.exception('WndMain.open_file(%s)', filename)
			dialogs.message_box_error(self,
					(_('Error opening file %s:\n') % filename) + err.message,
					_('Open file'))
			self.SetStatusText(_('Error: %s') % err.message)
			catalog = None

		else:
			if catalog is not None:
				if catalog.readonly:
					self.SetStatusText(_('Opened %s readonly') % filename)

				else:
					self.SetStatusText(_('Opened %s') % filename)

				dirty, dirtyp = catalog.dirty_objects_count
				_LOG.info('WndMain.open_file(%s) successfull dirty_object=%d/%d',
						filename, dirty, dirtyp)
				if dirtyp > 10:
					if dialogs.message_box_warning_yesno(self,
							_('Catalog file contain %d%% unused entries.\n' \
							'Rebuild catalog?') % dirtyp, _('Catalog')):
						if ecatalog.rebuild(catalog, self):
							self._save_catalog(catalog)

		finally:
			self.SetCursor(wx.STANDARD_CURSOR)

		self._update_menus_toolbars()

	def _update_last_open_files(self, filename=None):
		config = AppConfig()
		if filename is not None:
			config.add_last_open_file(filename)

		menu = self._main_menu_file_recent
		menulen = menu.GetMenuItemCount()
		for idx in xrange(menulen):
			menu.Remove(wx.ID_FILE1 + idx)

		last_open_files = config.last_open_files
		if len(last_open_files) > 0:
			for num, filepath in enumerate(last_open_files[:10]):
				filename = os.path.basename(filepath)
				menu.Append(wx.ID_FILE1 + num,
						"&%d. %s\tCTRL+%d" % (num + 1, filename, num + 1),
						_('Open %s') % filepath)

			self._main_menu_file_recent_item.Enable(True)

		else:
			self._main_menu_file_recent_item.Enable(False)

	def _save_catalog(self, catalog, force=False):
		''' Save @catalog when it's dirtry or @force'''
		self.SetCursor(wx.HOURGLASS_CURSOR)
		if catalog.dirty or force:
			try:
				Storage.save(catalog)

			except StandardError:
				_LOG.exception('WndMain._on_file_save(%s)', catalog.caption)
				dialogs.message_box_error(self,
						_('Error saving catalog %s') % catalog.catalog_filename,
						_('Save catalog'))

		self.SetCursor(wx.STANDARD_CURSOR)

	def _update_menus_toolbars(self):
		""" włączanie/wyłączanie pozycji menu/toolbar """
		catalog_loaded = not self.catalogs_not_loaded

		catalog_writable = False
		if catalog_loaded:
			selected_tree_item = self._dirs_tree.selected_item
			if selected_tree_item is None:
				catalog_writable = (not self._catalogs[0].readonly
						if len(self._catalogs) == 1 else False)

			else:
				catalog_writable = not selected_tree_item.catalog.readonly

		self._menu_bar.EnableTop(2, catalog_loaded)

		mm_items = self._main_menu_file.GetMenuItems()
		mm_items[2].Enable(catalog_loaded and catalog_writable)
		mm_items[4].Enable(catalog_loaded)
		mm_items[6].Enable(catalog_loaded and catalog_writable)
		mm_items[8].Enable(len(self._current_show_images) > 0)
		mm_items[9].Enable(len(self._current_show_images) > 0 \
				and epdf.EPDF_AVAILABLE)

		self._toolbar.EnableTool(self._tb_find, catalog_loaded)
		self._toolbar.EnableTool(self._tb_add_disk, catalog_loaded)
		self._toolbar.EnableTool(self._tb_save, catalog_loaded \
				and catalog_writable)

		if catalog_loaded:
			disk_selected = (isinstance(selected_tree_item, Disk)
				if selected_tree_item is not None else False)
			dir_selected = not disk_selected and selected_tree_item is not None \
					and isinstance(selected_tree_item, Directory)

			file_selected = self._photo_list.selected_count > 0

			mm_items = self._main_menu_catalog.GetMenuItems()
			mm_items[0].Enable(catalog_writable)
			mm_items[1].Enable(disk_selected and catalog_writable)
			mm_items[2].Enable(disk_selected and catalog_writable)
			mm_items[4].Enable(dir_selected and catalog_writable)
			mm_items[5].Enable(file_selected and catalog_writable)
			mm_items[7].Enable(file_selected and catalog_writable)

	def _update_settings(self):
		""" aktualizacja wszystkiego na podstawie ustawien """
		appconfig = AppConfig()
		self._photo_list.set_thumb_size(
				appconfig.get('settings', 'thumb_width', 200),
				appconfig.get('settings', 'thumb_height', 200))

		show_captions = appconfig.get('settings', 'view_show_captions', True)
		self._photo_list.show_captions = show_captions
		self._menu_view_show_captions.Check(show_captions)

		self._photo_list.thumbs_preload = appconfig.get('settings',
				'view_preload', True)
		self._photo_list.set_captions_font(
				dict(appconfig.get_items('settings') or []))
		self._photo_list.update()
		self._photo_list.Refresh()

		show_info = appconfig.get('settings', 'view_show_info', True)
		self._menu_view_show_info.Check(show_info)
		self._toggle_info_panel(show_info)
		self._photo_list.clear_cache()

	def _show_dir(self, images):
		'''  wyświetlenie zawartości katalogu lub listy

		@param images: Directory|[FileImage]|(FileImage) do wyświetlania;
				None oznacza odswieżenie aktualnego katalogu
		'''
		force_sort = False

		if images:
			if self._menu_view_show_recur.IsChecked() and hasattr(images,
					'images_recursive'):
				images = list(images.images_recursive)
				force_sort = True
			elif hasattr(images, 'files'):
				images = images.files


		if images is None or len(images) > 0:
			# jak sortujemy
			group_by = 0

			if self._menu_view_group_path.IsChecked(): # group_by_path
				group_by = 2
			elif self._menu_view_group_date.IsChecked(): #group_by_date
				group_by = 1

			self._photo_list.group_by = group_by
			force_sort |= group_by > 0 or images is None

			cmp_func = self._get_sort_function(False, force_sort)

			if images is None:
				# odświeżenie widoku
				self._photo_list.sort_current_dir(cmp_func)
			else:
				self._photo_list.show_dir(images, cmp_func)
				self._current_show_images = images

		else:
			self._photo_list.show_dir(images)
			self._current_show_images = images

		self._update_menus_toolbars()

	def __info_panel_clear(self):
		''' wyczyszczenie info-panelu '''
		if self._info_panel is not None:
			self._info_panel.clear()

	def _get_sort_function(self, images_as_list, force=True):
		'''zwraca fukncję sortowania miniaturek

		@params images_as_list - (bool) czy funkcja dla listy obiektów
				FileImage (true) czy lista obketów Thumb (false)
		@params force - (bool) - wymuszenie sortowania listy (domyślnie
				nie sortowna dla nazw)

		@return (funkcja klucza, reverse)
		'''
		desc = self._menu_view_sort_desc.IsChecked()
		sort_by = ecatalog.SORT_BY_DATE

		if self._menu_view_sort_name.IsChecked(): # sort by name
			if desc or images_as_list or force:
				sort_by = ecatalog.SORT_BY_NAME

			else:
				return None

		elif self._menu_view_group_path.IsChecked():
			sort_by = ecatalog.SORT_BY_PATH

		return ecatalog.get_sorting_function(sort_by, desc, images_as_list)


	def _show_item(self, item, show_info, images_count):
		try:
			self.SetCursor(wx.HOURGLASS_CURSOR)
			self._show_dir(item)
			if show_info:
				if self._info_panel is not None:
					self._info_panel.show_folder(item)
		finally:
			self.SetCursor(wx.STANDARD_CURSOR)
			if show_info:
				files_count, subdirs_count, dummy, dummy = item.directory_size
				self.SetStatusText(_('Directories %(dirs)d;  files: %(files)d') %
						dict(dirs=subdirs_count, files=files_count))
			else:
				self.SetStatusText(_('Files: %d') % images_count)


# vim: encoding=utf8: ff=unix:
