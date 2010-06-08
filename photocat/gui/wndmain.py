#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
MainWnd

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

	This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski, 2006-2010'
__revision__ = '$Id$'

__all__ = ['WndMain']


import os.path
import logging

import wx

from photocat.model import Collection, Directory, Disk, FileImage, Tag, \
		Timeline
from photocat.storage.storage import Storage
from photocat.engine import collections, eprint, epdf, os_helpers
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
from photocat.gui._dlgstats import DlgStats
from photocat.gui.components.thumbctrl import EVT_THUMB_DBCLICK, \
		EVT_THUMB_SELECTION_CHANGE

from .wndmain_view import WndMainView

_LOG = logging.getLogger(__name__)
_DEFAULT_ADD_OPTIONS = {
		'filter_folder_names': None,
		'include_empty': 0}
_THUMBS_CONFIRM_LIMIT = 1000


class WndMain(WndMainView):
	""" MainWnd """

	def __init__(self, app, debug):
		WndMainView.__init__(self, app, debug)
		_LOG.debug('MainWnd.__init__')

		self._collections = []
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
	def collections_not_loaded(self):
		''' Check is no collection loaded '''
		return not self._collections

	@property
	def selected_collection(self):
		''' get selected or first collection '''
		if self.collections_not_loaded:
			return None

		tree_selected = self._dirs_tree.selected_item
		collection = (self._collections[0] if tree_selected is None
				else tree_selected.collection)

		return collection

	############################################################################

	def _on_menu_close(self, evt):
		'''_on_menu_close'''
		self.Close()

	def _on_close(self, evt):
		'''_on_close'''
		dirty_collections = [collection for collection in self._collections
				if collection.dirty]

		if len(dirty_collections) > 0:
			for collection in dirty_collections:
				res = dialogs.message_box_not_save_confirm(self, collection.name)
				if res == wx.ID_CANCEL:
					return
				elif res == wx.ID_YES:
					self._save_collection(collection)

		for collection in self._collections:
			collections.collection_close(collection)

		del self._collections
		self._collections = None

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
		filename = dialogs.dialog_file_save(self, _('Collection file name'),
				'*.index', default_dir=self._last_used_dir)
		if filename is not None:
			if not filename.endswith('.index'):
				filename = filename + '.index'

			if collections.check_new_file_exists(filename)[0]:
				if not dialogs.message_box_question(self,
						_('Overwrite existing file?'),
						_("File %s already exist.\nAll data will be lost") % filename,
						_("Overwrite")):
					return

			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				collection = collections.new_collection(filename)
				self._collections.append(collection)
				self._dirs_tree.add_collection(collection)
			except StandardError, err:
				_LOG.exception('WndMain._on_file_new(%s)', filename)
				dialogs.message_box_error_ex(self, _("Cannot create new collection"),
						_('During creating file %(filename)s\n error occurred:%(error)s') \
						% dict(filename=filename, error=err.message))
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
			for cat in self._collections:
				self._save_collection(cat)
				self._dirs_tree.update_collection_node(cat)
		else:
			self._save_collection(tree_selected.collection)
			self._dirs_tree.update_collection_node(tree_selected.collection)

	def _on_file_close(self, evt):
		''' _on_file_close '''
		collection = self.selected_collection
		if collection is None:
			return

		if collection.dirty:
			res = dialogs.message_box_not_save_confirm(self, collection.name)
			if res == wx.ID_YES:
				self._save_collection(collection)
			elif res == wx.ID_CANCEL:
				return

		self._dirs_tree.delete_item(collection)
		collections.collection_close(collection)
		idx = [idx for idx, cat in enumerate(self._collections)
				if cat.name == collection.name]
		del self._collections[idx[0]]
		self._update_menus_toolbars()
		DlgSearchProvider().close_all()
		self._photo_list.clear_cache()

	def _on_file_rebuild(self, evt):
		''' _on_file_rebuild '''
		collection = self.selected_collection
		if collection is None:
			return
		if not dialogs.message_box_question(self,
				_('Rebuild collection %s?') % collection.name,
				_('This may take some time, but allow to reduce file size\n'
					'and improve performance.'), _("Rebuild")):
			return
		if collections.rebuild(collection, self):
			self._save_collection(collection)

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
		collection = self.selected_collection
		if collection is not None:
			collection.fill_shot_date()

	def _on_collection_add(self, evt):
		collection = self.selected_collection
		if collection is not None:
			disk = None
			try:
				disk = collections.add_disk_to_collection(collection, self)
			except StandardError:
				_LOG.exception('WndMain._on_collection_add()')
			else:
				if disk is not None:
					#self._save_collection(collection, True)
					self._dirs_tree.update_node_disk(disk)
					self._update_tags_timeline(collection)
					self._dirs_tree.update_collection_node(collection)

			self._update_menus_toolbars()

	def _on_collection_update_disk(self, evt):
		if self.collections_not_loaded:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			return

		disk = tree_selected.disk
		try:
			collections.update_disk_in_collection(disk.collection, disk, self)
		except StandardError:
			_LOG.exception('WndMain._on_collection_update_disk()')

		else:
			if disk is not None:
				collection = disk.collection
				#self._save_collection(collection, True)
				self._dirs_tree.update_node_disk(disk)
				self._update_tags_timeline(collection)
				self._dirs_tree.update_collection_node(collection)

			self._update_menus_toolbars()

	def _on_collection_del_disk(self, evt):
		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Disk):
			return
		if dialogs.message_box_delete_confirm(self, tree_selected.name):
			self._dirs_tree.delete_item(tree_selected)
			collection = tree_selected.collection
			collection.remove_disk(tree_selected)
			self._dirs_tree.update_collection_node(collection)
			self._update_tags_timeline(tree_selected.collection)
			self._update_menus_toolbars()

	def _on_collection_del_dir(self, evt):
		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			return
		if dialogs.message_box_delete_confirm(self, tree_selected.name):
			self._dirs_tree.delete_item(tree_selected)
			tree_selected.parent.remove_subdir(tree_selected)
			self._update_tags_timeline(tree_selected.collection)
			self._update_menus_toolbars()

	def _on_collection_del_image(self, evt):
		''' _on_collection_del_image '''
		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Collection):
			return
		selected_count = self._photo_list.selected_count
		if selected_count == 0:
			return

		text = ngettext("photo", "%(count)d photos", selected_count) % \
				dict(count=selected_count)
		if dialogs.message_box_delete_confirm(self, text):
			for image in self._photo_list.selected_items:
				folder.remove_file(image)

			self._show_dir(folder)
			if self._info_panel is not None:
				self._info_panel.show_folder(folder)

			self._dirs_tree.update_collection_node(folder.collection)

	def _on_collection_search(self, evt):
		''' _on_collection_search '''
		if not self.collections_not_loaded:
			DlgSearchProvider().create(self, self._collections,
					self._dirs_tree.selected_item).Show()

	def _on_collection_info(self, evt):
		''' _on_collection_info '''
		selectection = self._dirs_tree.selected_item
		if not selectection:
			selectection = self.selected_collection
		if selectection is not None:
			dlg = DlgStats(self, selectection)
			dlg.ShowModal()
			dlg.Destroy()

	def _on_collection_edit_multi(self, evt):
		''' _on_collection_edit_multi'''
		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Collection) or \
				len(folder.files) == 0:
			return

		image = FileImage(None, None, None, None, collection=folder.collection)
		result = {}
		dlg = DlgPropertiesMulti(self, image, result)
		if dlg.ShowModal() == wx.ID_OK:
			changed_tags = collections.update_images_from_dict(
					self._photo_list.selected_items, result)
			folder.collection.dirty = True
			self._dirs_tree.update_collection_node(folder.collection)
			self._update_changed_tags(folder.collection.tags_provider, changed_tags)

		dlg.Destroy()

	def _on_collection_edit_tags(self, evt):
		if self.collections_not_loaded:
			return

		collection = self.selected_collection
		if show_dlg_edit_tags(self, collection.tags_provider):
			collection.dirty = True
			self._dirs_tree.update_collection_node(collection)
			self._update_tags_timeline(collection)

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
			elif images_count > _THUMBS_CONFIRM_LIMIT:
				# jeżeli ilość plików > 1000 - ostrzeżenie i pytania
				if not dialogs.message_box_question(self,
						_("Show %d photos?") % images_count,
						_("Showing that many photos may take a long time."),
						_("Show")):
					self._show_dir([])
					count = len(item.files)
					status = ngettext("One photo", "%(count)d photos", count)
					self.SetStatusText(status % {'count': count})
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

		if isinstance(item, Collection):
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
			item.collection.dirty = True
			if self._info_panel is not None:
				self._info_panel.show_folder(item)

			if isinstance(item, Disk):
				self._dirs_tree.update_node_disk(item, False)
			else:
				self._dirs_tree.update_node_directory(item, False)

			self._dirs_tree.update_collection_node(item.collection)
			self._update_changed_tags(item.collection.tags_provider, dlg.changed_tags)

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
				selected.collection.dirty = True
				self._dirs_tree.update_collection_node(selected.collection)
				self._update_changed_tags(selected.collection.tags_provider,
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
		if self.collections_not_loaded:
			return

		if evt.GetKeyCode() == wx.WXK_DELETE:
			tree_selected = self._dirs_tree.selected_item
			if tree_selected is None:
				return
			if isinstance(tree_selected, Disk):
				self._on_collection_del_disk(None)
			elif isinstance(tree_selected, Directory):
				self._on_collection_del_dir(None)

	def _on_dirtree_right_down(self, evt):
		pos = evt.GetPosition()
		item, _flags = self._dirs_tree.HitTest(pos)
		if item:
			self._dirs_tree.SelectItem(item)
		evt.Skip()

	def _on_photolist_key_down(self, evt):
		if evt.m_keyCode == wx.WXK_DELETE:
			self._on_collection_del_image(None)
		evt.Skip()

	def _on_photolist_popupmenu(self, evt):
		if self._photo_list.selected_item:
			self._photo_list.PopupMenu(self._create_popup_menu_image(),
					evt.GetPosition())

	def _on_photo_popoup_properties(self, evt):
		selected_count = self._photo_list.selected_count
		if selected_count > 1:
			self._on_collection_edit_multi(evt)
		elif selected_count == 1:
			self._on_thumb_dclick(evt)

	def _on_photo_popoup_open(self, evt):
		selected = self._photo_list.selected_item
		if selected and selected.disk.last_path:
			os_helpers.open_file(os.path.join(selected.disk.last_path,
				selected.path))

	def _on_zoom_scroll(self, evt):
		self._set_zoom()

	############################################################################

	def open_file(self, filename):
		''' Open collection
		@filename: full path to the index file
		'''
		if filename in (cat.filename for cat in self._collections):
			return

		try:
			self.SetStatusText(_('Opening %s....  Please wait...') % filename)
			self.SetCursor(wx.HOURGLASS_CURSOR)
			collection = collections.open_collection(filename)
			self._collections.append(collection)
			self._dirs_tree.add_collection(collection)
			self._update_last_open_files(filename)
			self.SetStatusText(filename)
		except StandardError, err:
			_LOG.exception('WndMain.open_file(%s)', filename)
			dialogs.message_box_error_ex(self,
					_('Cannot open file'),
					_('During opening file %(filename)s\nerror occurred: %(error)s') % \
					dict(filename=filename, error=err.message))
			self.SetStatusText(_('Error: %s') % err.message)
			collection = None
		else:
			if collection is not None:
				if collection.readonly:
					self.SetStatusText(_('Opened %s readonly') % filename)
				else:
					self.SetStatusText(_('Opened %s') % filename)

				dirty, dirtyp = collection.dirty_objects_count
				_LOG.info('WndMain.open_file(%s) successful dirty_object=%d/%d',
						filename, dirty, dirtyp)
				if dirtyp > 10:
					if dialogs.message_box_question(self,
							_('Collection file contain %d%% unused entries.\n'
								'Rebuild collection?') % dirtyp,
							_('This may take some time, but allow to reduce file size\n'
								'and improve performance.'), _("Rebuild")):
						if collections.rebuild(collection, self):
							self._save_collection(collection)
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

	def _save_collection(self, collection, force=False):
		''' Save @collection when it's dirty or @force'''
		self.SetCursor(wx.HOURGLASS_CURSOR)
		if collection.dirty or force:
			try:
				Storage.save(collection)
			except StandardError:
				_LOG.exception('WndMain._on_file_save(%s)', collection.caption)
				dialogs.message_box_error(self,
						_('Error saving collection %s') % collection.filename,
						_('Save collection'))

		self.SetCursor(wx.STANDARD_CURSOR)

	def _update_menus_toolbars(self):
		""" włączanie/wyłączanie pozycji menu/toolbar """
		collections_loaded = not self.collections_not_loaded

		collection_writable = False
		if collections_loaded:
			selected_tree_item = self._dirs_tree.selected_item
			if selected_tree_item is None:
				collection_writable = (not self._collections[0].readonly
						if len(self._collections) == 1 else False)
			else:
				collection_writable = not selected_tree_item.collection.readonly
		images_showed = len(self._current_show_images) > 0

		mm_items = self._main_menu_file.GetMenuItems()
		mm_items[3].Enable(collection_writable)
		mm_items[4].Enable(collection_writable)
		mm_items[6].Enable(images_showed and epdf.EPDF_AVAILABLE)
		mm_items[7].Enable(images_showed)
		mm_items[9].Enable(collections_loaded)
		self._toolbar.EnableTool(self._tb_find, collections_loaded)
		self._toolbar.EnableTool(self._tb_add_disk, collections_loaded)
		self._toolbar.EnableTool(self._tb_save, collection_writable)

		if collections_loaded:
			disk_selected = (isinstance(selected_tree_item, Disk)
					if selected_tree_item is not None else False)
			dir_selected = not disk_selected and selected_tree_item is not None \
					and isinstance(selected_tree_item, Directory)

			file_selected = self._photo_list.selected_count > 0
			mm_items = self._main_menu_collection.GetMenuItems()
			mm_items[0].Enable(collection_writable)
			mm_items[1].Enable(disk_selected and collection_writable)
			mm_items[2].Enable(disk_selected and collection_writable)
			mm_items[4].Enable(dir_selected and collection_writable)
			mm_items[6].Enable(file_selected and collection_writable)
			mm_items[7].Enable(file_selected and collection_writable)
			mm_items[9].Enable(True)
			mm_items[11].Enable(True)
		else:
			mitems = self._main_menu_collection.GetMenuItems()
			for idx in xrange(len(mitems) - 1):
				mitems[idx].Enable(False)

	def _update_settings(self):
		""" aktualizacja wszystkiego na podstawie ustawien """
		self._set_zoom()

		appconfig = AppConfig()
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

	def _set_zoom(self):
		zidx = self._s_zoom.GetValue()
		zfac = (0.25, 0.5, 0.75, 1, 1.5, 2)[zidx]
		appconfig = AppConfig()
		self._photo_list.set_thumb_size(
				int(appconfig.get('settings', 'thumb_width', 200) * zfac),
				int(appconfig.get('settings', 'thumb_height', 200) * zfac),
				zfac)
		self._s_zoom_label.SetLabel(' %d%%' % (zfac * 100))

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

			if self._menu_view_group_path.IsChecked():  # group_by_path
				group_by = 2
			elif self._menu_view_group_date.IsChecked():  # group_by_date
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
		sort_by = collections.SORT_BY_DATE

		if self._menu_view_sort_name.IsChecked():		# sort by name
			if desc or images_as_list or force:
				sort_by = collections.SORT_BY_NAME
			else:
				return None
		elif self._menu_view_group_path.IsChecked():
			sort_by = collections.SORT_BY_PATH

		return collections.get_sorting_function(sort_by, desc, images_as_list)

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
				f_count, sd_count, dummy, dummy = item.directory_size
				dirs = ngettext("One directory", "%(count)d directories", sd_count) % \
						{'count': sd_count}
				files = ngettext("one photo", "%(count)d photos", f_count) % \
						{'count': f_count}
				status = dirs + ', ' + files
			else:
				status = ngettext("One photo", "%(count)d photos", images_count) % \
						{'count': images_count}
			self.SetStatusText(status)


# vim: encoding=utf8: ff=unix:
