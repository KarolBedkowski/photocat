#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
MainWnd

 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004-2007

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

__all__			= ['WndMain']



import os.path
import logging
_LOG = logging.getLogger(__name__)

import wx

from kabes.tools.appconfig		import AppConfig
from kabes.wxtools				import dialogs
from kabes.wxtools.iconprovider	import IconProvider
from kabes.wxtools.guitools		import create_menu, create_toolbar_button, create_menu_item
from kabes.wxtools.wnd_shell	import WndShell

import pc

from pc.model				import Catalog, Directory, Disk, FileImage, Tag, Timeline
from pc.storage.storage		import Storage
from pc.engine				import ecatalog, eprint, epdf, image

from components.dirstree	import DirsTree
from components.infopanel	import InfoPanel
from components.thumbctrl	import ThumbCtrl, EVT_THUMB_DBCLICK, EVT_THUMB_SELECTION_CHANGE

from _dlgabout				import show_about_box
from _dlgproperties			import DlgProperties
from _dlgproperties_dir		import DlgPropertiesDir
from _dlgproperties_disk	import DlgPropertiesDisk
from _dlgproperties_mutli	import DlgPropertiesMulti
from _dlgsearch				import DlgSearchProvider
from _dlgsettings			import DlgSettings
from _dlg_edit_tags			import show_dlg_edit_tags

_ = wx.GetTranslation

_DEFAULT_ADD_OPTIONS = {
		'filter_folder_names': None,
		'include_empty': 0
}



class WndMain(wx.Frame):
	""" MainWnd """

	def __init__(self, app, debug):
		_LOG.debug('MainWnd.__init__')

		appconfig = AppConfig()
		size = appconfig.get('main_wnd', 'size', (800, 600))

		wx.Frame.__init__(self, None, -1, "PC %s" % pc.__version__, size=size)

		self._debug			= debug
		self._app			= app

		self._catalogs		= []
		self._layout_splitter	= None
		self._info_panel_size = None
		self._last_used_dir = os.path.expanduser('~')

		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['folder_image'])

		self.SetIcon(self._icon_provider.get_icon('folder_image'))

		self.SetMenuBar(self._create_main_menu())
		self._create_toolbar()
		self._create_layout(appconfig)
		self.CreateStatusBar(2, wx.ST_SIZEGRIP)
		self.SetStatusWidths([-1, 50])

		self._print_data			= wx.PrintData()
		self._current_show_images	= []

		position = appconfig.get('main_wnd', 'position')
		if position is None:
			self.Centre(wx.BOTH)
		else:
			self.Move(position)

		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Bind(wx.EVT_SIZE, self._on_size)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_dirtree_item_select, self._dirs_tree)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_dirtree_item_activate, self._dirs_tree)
		self._photo_list.Bind(EVT_THUMB_SELECTION_CHANGE, self._on_thumb_sel_changed)
		self._photo_list.Bind(EVT_THUMB_DBCLICK, self._on_thumb_dclick)
		self.Bind(wx.EVT_MENU_RANGE, self._on_file_history, id=wx.ID_FILE1, id2=wx.ID_FILE9)
		self.Bind(wx.EVT_TREE_ITEM_MENU	, self._on_dirtree_context_menu, self._dirs_tree)
		self._dirs_tree.Bind(wx.EVT_RIGHT_DOWN, self._on_dirtree_right_down, self._dirs_tree)
		self._dirs_tree.Bind(wx.EVT_KEY_DOWN, self._on_dirtree_key_down)
		self._photo_list.Bind(wx.EVT_CHAR, self._on_photolist_key_down)
		self._photo_list.Bind(wx.EVT_RIGHT_UP, self._on_photolist_popupmenu)

		self.__update_last_open_files()
		self.__update_menus_toolbars()
		self.__update_settings()


	#########################################################################################################


	@property
	def catalogs_not_loaded(self):
		return not self._catalogs


	@property
	def selected_catalog(self):
		if self.catalogs_not_loaded:
			return None

		tree_selected = self._dirs_tree.selected_item
		catalog = self._catalogs[0] if tree_selected is None else tree_selected.catalog

		return catalog


	#########################################################################################################


	def _create_layout(self, appconfig):
		splitter = self._layout_splitter_v = wx.SplitterWindow(self, -1, style=wx.SW_BORDER)

		splitter2 = self._layout_splitter_h = wx.SplitterWindow(splitter, -1, style=wx.SW_BORDER)
		splitter2.SplitHorizontally(self._create_layout_photolist(splitter2), self._create_layout_info(splitter2))
		splitter2.SetMinimumPaneSize(0)

		splitter.SplitVertically(self._create_layout_tree(splitter), splitter2)

		splitter.SetSashGravity(0.0)
		splitter2.SetSashGravity(1.0)

		splitter.SetSashPosition(appconfig.get('main_wnd', 'splitter_v', 200))
		splitter2.SetSashPosition(appconfig.get('main_wnd', 'splitter_h', -1))


	def _create_main_menu(self):
		self.__menu_bar = menu_bar = wx.MenuBar()
		menu_bar.Append(self._create_main_menu_file(),		_('&File'))
		menu_bar.Append(self._create_main_menu_view(),		_('&View'))
		menu_bar.Append(self._create_main_menu_catalog(),	_('&Catalog'))
		menu_bar.Append(self._create_main_menu_help(),		wx.GetStockLabel(wx.ID_HELP, True))
		if self._debug:
			menu_bar.Append(self._create_main_menu_debug(),	'&Debug')

		return menu_bar


	def _create_main_menu_file(self):
		self._main_menu_file = create_menu(self, (
			(None,	'Ctrl-N',	_('Create new catalog'),	self._on_file_new,		wx.ID_NEW,		wx.ART_NEW),
			(None,	'Ctrl+O',	_('Load catalog'),			self._on_file_open,		wx.ID_OPEN,		wx.ART_FILE_OPEN),
			(None,	'Ctrl+S',	_('Save current catalog'),	self._on_file_save,		wx.ID_SAVE,		wx.ART_FILE_SAVE),
			(_('Close catalog'),	'Ctrl+W',	_('Close current catalog'),	self._on_file_close),
			('-'),
			(_('Rebuild catalog'),	None,		_('Rebuild catalog'),		self._on_file_rebuild),
			('-'),
			(None,	'Ctrl+P',	'',							self._on_file_print_prv, wx.ID_PRINT, 	wx.ART_PRINT),
			(_('Export to PDF...'),	None,		'',							self._on_file_export_pdf),
			('-'),
			(_('Program settings'),	None,		_('Program settings'),		self._on_file_settings),
			('-'),
			(None,	'Alt-F4',	_('Close application'),		self._on_close,			wx.ID_EXIT,		wx.ART_QUIT)
		))

		self._main_menu_file_recent = wx.Menu()
		self._main_menu_file_recent_item = self._main_menu_file.InsertMenu(3, -1, _('Recent files'),
				self._main_menu_file_recent)

		return self._main_menu_file


	def _create_main_menu_catalog(self):
		menu = create_menu(self, (
			(_('&Add disk...'),		None,	_('Add disk to catalog'),				self._on_catalog_add,		None,	wx.ART_NEW_DIR),
			(_('&Update disk...'),	None,	_('Update selected disk'),				self._on_catalog_update_disk),
			(_('&Delete disk...'),	None,	_('Delete selected disk from catalog'),	self._on_catalog_del_disk,	None,	wx.ART_DELETE),
			('-'),
			(_('Delete selected &dir...'),	None,	'',								self._on_catalog_del_dir),
			(_('Delete selected &image...'),	None,	'',							self._on_catalog_del_image),
			('-'),
			(_('&Edit selected files...'),	None,	'',								self._on_catalog_edit_multi),
			('-'),
			(None,				'Ctrl+F',	_('Search in calalogs'),				self._on_catalog_search,	wx.ID_FIND,	wx.ART_FIND),
			(_('Info'),			None,		_('About selected calalog...'),			self._on_catalog_info),
			(_('Tags'),			None,		_('Manage taglist...'),					self._on_catalog_edit_tags),
		))
		self._main_menu_catalog = menu
		return menu


	def _create_main_menu_view(self):
		menu = wx.Menu()

		self._menu_view_show_info = create_menu_item(self, menu,
				_('[x]Show &info'),		self._on_view_show_hide_info,		accel='F4')[1]
		self._menu_view_show_captions = create_menu_item(self, menu,
				_('[x]Show &captions'),	self._on_view_show_hide_captions)[1]

		menu.AppendSeparator()

		self._menu_view_sort_name = create_menu_item(self, menu, _('[o]Sort by &name '),	self._on_view_sort)[1]
		self._menu_view_sort_date = create_menu_item(self, menu, _('[o]Sort by &date '),	self._on_view_sort)[1]
		self._menu_view_group_date = create_menu_item(self, menu, _('[o]&Group by date '),	self._on_view_sort)[1]
		self._menu_view_group_path = create_menu_item(self, menu, _('[o]&Group by path '),	self._on_view_sort)[1]

		menu.AppendSeparator()

		self._menu_view_sort_desc = create_menu_item(self, menu, _('[x]Sort descend'),		self._on_view_sort)[1]
		self._menu_view_show_recur = create_menu_item(self, menu, _('[x]With subdirs'),		self._on_view_sort)[1]

		return menu


	def _create_main_menu_help(self):
		menu = create_menu(self, (
			(_('&About...'),	None,	'',	self._on_help_about,	wx.ID_ABOUT,	wx.ART_INFORMATION),
		))
		return menu


	def _create_main_menu_debug(self):
		menu = create_menu(self, (
			('Shell', 'Ctrl+L', '', self._on_debug_shell, None),
			('Fill shot date', None, '', self._on_debug_fill_shot_date, None),
		))
		return menu


	def _create_toolbar(self):
		''' Utworzenie toolbar-a '''
		self.__toolbar = toolbar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER|wx.TB_FLAT|wx.TB_TEXT)
		toolbar.SetToolBitmapSize((16, 16))

		#def cbtn(label, function, iconname, description=''):
		#	return create_toolbar_button(toolbar, label, function, self._icon_provider.get_image(iconname),
		#			description=description)

		def cbtna(label, function, iconname, description=''):
			return create_toolbar_button(toolbar, label, function, imgid=iconname, description=description)

		cbtna(wx.ID_NEW,	self._on_file_new,	wx.ART_NEW,			_('Create new catalog'))
		cbtna(wx.ID_OPEN,	self._on_file_open,	wx.ART_FILE_OPEN,	_('Load catalog'))
		self.__tb_save = cbtna(wx.ID_SAVE,	self._on_file_save,	wx.ART_FILE_SAVE,	_('Save catalog'))

		toolbar.AddSeparator()

		self.__tb_find = cbtna(wx.ID_FIND,	self._on_catalog_search, wx.ART_FIND,	_('Search in calalogs'))

		toolbar.AddSeparator()

		self.__tb_add_disk = cbtna(_('Add disk...'),	self._on_catalog_add,	wx.ART_NEW_DIR,	_('Add disk to catalog'))

		toolbar.AddSeparator()
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


	#########################################################################################################


	def _on_close(self, evt):
		dirty_catalogs = [ catalog for catalog in self._catalogs if catalog.dirty ]

		if len(dirty_catalogs) > 0:
			for catalog in dirty_catalogs:
				res = dialogs.message_box_warning_yesnocancel(self,
						_("Catalog %s isn't saved\nSave it?") % catalog.caption, 'PC')

				if res == wx.ID_CANCEL:
					return

				elif res == wx.ID_YES:
					self.__save_catalog(catalog)

		elif not dialogs.message_box_question_yesno(self, _('Close program?'), 'PC'):
			return

		for catalog in self._catalogs:
			ecatalog.catalog_close(catalog)

		appconfig = AppConfig()
		appconfig.set('main_wnd', 'size',		self.GetSizeTuple())
		appconfig.set('main_wnd', 'position',	self.GetPositionTuple())
		appconfig.set('main_wnd', 'splitter_h', self._layout_splitter_h.GetSashPosition())
		appconfig.set('main_wnd', 'splitter_v', self._layout_splitter_v.GetSashPosition())

		self._app.ExitMainLoop()
		evt.Skip()


	def _on_size(self, evt):
		self._dirs_tree.Refresh()
		evt.Skip()


	def _on_file_new(self, evt):
		if dialogs.message_box_question_yesno(self, _('Create new catalog?'), 'PC'):
			filename = dialogs.dialog_file_save(self, _('Catalog file name'), '*.index', default_dir=self._last_used_dir)
			if filename is not None:
				if not filename.endswith('.index'):
					filename = filename + '.index'

				if ecatalog.check_new_file_exists(filename)[0]:
					if not dialogs.message_box_question_yesno(self, _('File exists!\nOverwrite?'), 'PC'):
						return

				try:
					self.SetCursor(wx.HOURGLASS_CURSOR)
					catalog = ecatalog.new_catalog(filename)
					self._catalogs.append(catalog)
					self._dirs_tree.add_catalog(catalog)

				except Exception, err:
					_LOG.exception('WndMain._on_file_new(%s)', filename)
					dialogs.message_box_error(self, (_('Error opening file %s:\n') % filename) + err.message, _('New file'))
					self.SetStatusText(_('Error: %s') % err.message)

				else:
					self.__update_last_open_files(filename)
					self.__update_menus_toolbars()
					self._last_used_dir = os.path.dirname(filename)

				finally:
					self.SetCursor(wx.STANDARD_CURSOR)


	def _on_file_open(self, evt):
		filename = dialogs.dialog_file_load(self, _('Open file'), '*.index', default_dir=self._last_used_dir)
		if filename is not None:
			if not filename.endswith('.index'):
				filename = filename + '.index'

			self._open_file(filename)
			self.__update_menus_toolbars()
			self._last_used_dir = os.path.dirname(filename)


	def _on_file_save(self, evt):
		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			for cat in self._catalogs:
				self.__save_catalog(cat)
				self._dirs_tree.update_catalog_node(cat)

		else:
			self.__save_catalog(tree_selected.catalog)
			self._dirs_tree.update_catalog_node(tree_selected.catalog)


	def _on_file_close(self, evt):
		catalog = self.selected_catalog
		if catalog is None:
			return

		if catalog.dirty:
			res = dialogs.message_box_warning_yesnocancel(self,
					_('Catalog %s has unsaved changes!\nSave before close??') % catalog.caption,
					'PC')

			if res == wx.ID_YES:
				self.__save_catalog(catalog)

			elif res == wx.ID_CANCEL:
				return

		elif not dialogs.message_box_question_yesno(self, _('Close catalog %s?') % catalog.caption, 'PC'):
			return

		self._dirs_tree.delete_item(catalog)
		ecatalog.catalog_close(catalog)
		self._catalogs.remove(catalog)
		self.__update_menus_toolbars()
		DlgSearchProvider().close_all()


	def _on_file_rebuild(self, evt):
		catalog = self.selected_catalog
		if catalog is None:
			return

		if not dialogs.message_box_question_yesno(self, _('Rebuild catalog %s?') % catalog.caption, 'PC'):
			return

		if ecatalog.rebuild(catalog, self):
			self.__save_catalog(catalog)


	def _on_file_settings(self, evt):
		dlg = DlgSettings(self)
		if dlg.ShowModal() == wx.ID_OK:
			self.__update_settings()

		dlg.Destroy()


	def _on_file_export_pdf(self, evt):
		if len(self._current_show_images) > 0 and epdf.EPDF_AVAILABLE:
			sort_key_func, reverse = self.__get_sort_function(True, True)
			images = sorted(self._current_show_images, key=sort_key_func, reverse=reverse)
			options = {
					'show_captions': self._photo_list.show_captions,
					'group_by': 	self._photo_list.group_by
			}
			epdf.create_pdf(self, images, options)


	def _on_file_print_prv(self, evt):
		if len(self._current_show_images) > 0:
			sort_key_func, reverse = self.__get_sort_function(True, True)
			images = sorted(self._current_show_images, key=sort_key_func, reverse=reverse)

			appconfig = AppConfig()
			options = {
				'fontdata':		dict(appconfig.get_items('settings') or []),
				'thumb_width':	self._photo_list.thumb_width,
				'thumb_height': self._photo_list.thumb_height,
				'show_captions': self._photo_list.show_captions,
				'group_by': 	self._photo_list.group_by
			}
			eprint.print_preview(self, self._print_data, images, options)


	def _on_view_show_hide_info(self, evt):
		""" wybór z menu widok->pokaż/ukryj info """
		AppConfig().set('settings', 'view_show_info', self._menu_view_show_info.IsChecked())
		self._toggle_info_panel()


	def _on_view_show_hide_captions(self, evt):
		""" wybór z menu widok->pokaż/ukryj podpisy """
		show_captions = self._menu_view_show_captions.IsChecked()
		AppConfig().set('settings', 'view_show_captions', show_captions)
		self._photo_list.show_captions	= show_captions
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

			except Exception:
				_LOG.exception('WndMain._on_catalog_add()')

			else:
				if disk is not None:
					#self.__save_catalog(catalog, True)
					self._dirs_tree.update_node_disk(disk)
					self.__update_tags_timeline(catalog)
					self._dirs_tree.update_catalog_node(catalog)

			self.__update_menus_toolbars()


	def _on_catalog_update_disk(self, evt):
		if self.catalogs_not_loaded:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			return

		disk = tree_selected.disk
		try:
			ecatalog.update_disk_in_catalog(disk.catalog, disk, self)

		except Exception, err:
			_LOG.exception('WndMain._on_catalog_update_disk()')

		else:
			if disk is not None:
				catalog = disk.catalog
				#self.__save_catalog(catalog, True)
				self._dirs_tree.update_node_disk(disk)
				self.__update_tags_timeline(catalog)
				self._dirs_tree.update_catalog_node(catalog)

			self.__update_menus_toolbars()


	def _on_catalog_del_disk(self, evt):
		if self.catalogs_not_loaded:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Disk):
			dialogs.message_box_error(self, _('No disk selected'), _('Delete disk'))
			return

		if dialogs.message_box_warning_yesno(self, _('Delete disk %s?') % tree_selected.name, 'PC'):
			self._dirs_tree.delete_item(tree_selected)
			catalog = tree_selected.catalog
			catalog.remove_disk(tree_selected)
			self._dirs_tree.update_catalog_node(catalog)
			self.__update_tags_timeline(tree_selected.catalog)
			self.__update_menus_toolbars()


	def _on_catalog_del_dir(self, evt):
		if self.catalogs_not_loaded:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			dialogs.message_box_error(self, _('No directory selected'), _('Delete directory'))
			return

		if dialogs.message_box_warning_yesno(self, _('Delete directory %s?') % tree_selected.name, 'PC'):
			self._dirs_tree.delete_item(tree_selected)
			tree_selected.parent.remove_subdir(tree_selected)
			self.__update_tags_timeline(tree_selected.catalog)
			self.__update_menus_toolbars()


	def _on_catalog_del_image(self, evt):
		if self.catalogs_not_loaded:
			return

		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Catalog):
			return

		selected_count = self._photo_list.selected_count
		if selected_count == 0:
			return

		if dialogs.message_box_warning_yesno(self, _('Delete %d images?') % selected_count, 'PC'):
			for image in self._photo_list.selected_items:
				folder.remove_file(image)

			self._show_dir(folder)
			if self._info_panel is not None:
				self._info_panel.show_folder(folder)

			self._dirs_tree.update_catalog_node(folder.catalog)


	def _on_catalog_search(self, evt):
		if not self.catalogs_not_loaded:
			DlgSearchProvider().create(self, self._catalogs, self._dirs_tree.selected_item).Show()


	def _on_catalog_info(self, evt):
		if self.catalogs_not_loaded:
			return

		catalog = self.selected_catalog

		files_count, subdirs_count = 0, 0
		for disk in catalog.disks:
			disk_files_count, disk_subdirs_count, disk_files_count2, disk_subdirs_count2 = disk.directory_size
			files_count		+= disk_files_count		+ disk_files_count2
			subdirs_count	+= disk_subdirs_count	+ disk_subdirs_count2

		dirty, dirtyp = catalog.dirty_objects_count

		data = dict(disks=len(catalog.disks), files=files_count, dirs=subdirs_count, dirty=dirty, dirtyp=dirtyp)
		info = _('Disks: %(disks)d\nDirs: %(dirs)d\nFiles: %(files)d\nDirty entries: %(dirty)d (%(dirtyp)d%%)') % data
		dialogs.message_box_info(self, info, 'PC')


	def _on_catalog_edit_multi(self, evt):
		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Catalog) or len(folder.files) == 0:
			return

		image = FileImage(None, None, None, None, catalog=folder.catalog)

		result = {}

		dlg = DlgPropertiesMulti(self, image, result)
		if dlg.ShowModal() == wx.ID_OK:
			changed_tags = Catalog.update_images_from_dict(self._photo_list.selected_items, result)
			folder.catalog.dirty = True
			self._dirs_tree.update_catalog_node(folder.catalog)
			self.__update_changed_tags(folder.catalog.tags_provider, changed_tags)

		dlg.Destroy()


	def _on_catalog_edit_tags(self, evt):
		if self.catalogs_not_loaded:
			return

		catalog = self.selected_catalog
		if show_dlg_edit_tags(self, catalog.tags_provider):
			catalog.dirty = True
			self._dirs_tree.update_catalog_node(catalog)
			self.__update_tags_timeline(catalog)


	def _on_dirtree_item_select(self, evt):
		item = self._dirs_tree.selected_item
		show_info = True
		images_count = 0

		self.__info_panel_clear()
		self.__update_menus_toolbars()

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
						_('Number of files exceed 1000!\nShow %d files?') % len(item.files), 'PC'):
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

		if self._info_panel is not None:
			if isinstance(item, Directory):
				self._info_panel.show_folder(item)

			else:
				self._info_panel.clear()


	def _on_dirtree_item_activate(self, evt):
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
			self.__update_changed_tags(item.catalog.tags_provider, dlg.changed_tags)

		dlg.Destroy()


	def _on_thumb_sel_changed(self, evt):
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

		self.__update_menus_toolbars()


	def _on_thumb_dclick(self, evt):
		selected_idx, items_count = self._photo_list.selected_index
		items_count -= 1
		while selected_idx > -1:
			selected = self._photo_list.get_item_by_index(selected_idx)
			dlg = DlgProperties(self, selected, show_next_prev=(selected_idx>0, selected_idx<items_count))
			result = dlg.ShowModal()
			dlg.Destroy()
			if result == wx.ID_OK:
				if self._info_panel is not None:
					self._info_panel.show(selected)

				selected.catalog.dirty = True
				self._dirs_tree.update_catalog_node(selected.catalog)
				self.__update_changed_tags(selected.catalog.tags_provider, dlg.changed_tags)

				break

			elif result == wx.ID_BACKWARD:
				selected_idx -=1

			elif result == wx.ID_FORWARD:
				selected_idx +=1

			else:
				break




	def _on_file_history(self, evt):
		filehistnum = evt.GetId() - wx.ID_FILE1
		filename = AppConfig().last_open_files[filehistnum]
		self._open_file(filename)


	def _on_dirtree_context_menu(self, evt):
		tree_item = evt.GetItem()
		if tree_item is not None and tree_item.IsOk():
			item = self._dirs_tree.GetItemData(tree_item)
			if item is not None:
				data = item.GetData()
				if data is not None:
					self.PopupMenu(self.__create_popup_menu(data))


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
		pt = evt.GetPosition()
		item, _flags = self._dirs_tree.HitTest(pt)
		if item:
			self._dirs_tree.SelectItem(item)

		evt.Skip()


	def _on_photolist_key_down(self, evt):
		if evt.m_keyCode == wx.WXK_DELETE:
			self._on_catalog_del_image(None)

		evt.Skip()


	def _on_photolist_popupmenu(self, evt):
		if self._photo_list.selected_item:
			self._photo_list.PopupMenu(self.__create_popup_menu_image(), evt.GetPosition())


	def _on_photo_popoup_properties(self, evt):
		selected_count = self._photo_list.selected_count
		if selected_count > 1:
			self._on_catalog_edit_multi(evt)

		elif selected_count == 1:
			self._on_thumb_dclick(evt)

	################################################################################


	def _open_file(self, filename):
		if filename in ( cat.catalog_filename for cat in self._catalogs ):
			return

		try:
			self.SetStatusText(_('Opening %s....  Please wait...') % filename)
			self.SetCursor(wx.HOURGLASS_CURSOR)
			catalog = ecatalog.open_catalog(filename)
			self._catalogs.append(catalog)
			self._dirs_tree.add_catalog(catalog)
			self.__update_last_open_files(filename)
			self.SetStatusText(filename)

		except Exception, err:
			_LOG.exception('WndMain._open_file(%s)', filename)
			dialogs.message_box_error(self, (_('Error opening file %s:\n') % filename) + err.message, _('Open file'))
			self.SetStatusText(_('Error: %s') % err.message)
			catalog = None

		else:
			if catalog is not None:
				if catalog.readonly:
					self.SetStatusText(_('Opened %s readonly') % filename)

				else:
					self.SetStatusText(_('Opened %s') % filename)

				dirty, dirtyp = catalog.dirty_objects_count
				_LOG.info('WndMain._open_file(%s) successfull dirty_object=%d/%d', filename, dirty, dirtyp)
				if dirtyp > 10:
					if dialogs.message_box_warning_yesno(self,
							_('Catalog file contain %d%% unused entries.\nRebuild catalog?') % dirtyp, 'PC'):
						if ecatalog.rebuild(catalog, self):
							self.__save_catalog(catalog)

		finally:
			self.SetCursor(wx.STANDARD_CURSOR)

		self.__update_menus_toolbars()


	def __update_last_open_files(self, filename=None):
		config = AppConfig()
		if filename is not None:
			config.add_last_open_file(filename)

		menu = self._main_menu_file_recent
		menulen = menu.GetMenuItemCount()
		for x in xrange(menulen):
			menu.Remove(wx.ID_FILE1 + x)

		last_open_files = config.last_open_files
		if len(last_open_files) > 0:
			for num, filepath in enumerate(last_open_files[:10]):
				filename = os.path.basename(filepath)
				menu.Append(wx.ID_FILE1+num, "&%d. %s\tCTRL+%d" % (num+1, filename, num+1),
						_('Open %s') % filepath)

			self._main_menu_file_recent_item.Enable(True)

		else:
			self._main_menu_file_recent_item.Enable(False)


	def __save_catalog(self, catalog, force=False):
		self.SetCursor(wx.HOURGLASS_CURSOR)
		if catalog.dirty or force:
			try:
				Storage.save(catalog)

			except:
				_LOG.exception('WndMain._on_file_save(%s)', catalog.caption)
				dialogs.message_box_error(self, _('Error saving catalog %s') % catalog.catalog_filename, _('Save catalog'))

		self.SetCursor(wx.STANDARD_CURSOR)


	def show_item(self, folder):
		''' wndmain.show_item(folder) -- wyświetlenia podanego folderu '''
		self._dirs_tree.show_node(folder)
		self._dirs_tree.SelectItem(folder.tree_node)


	def select_item(self, item):
		''' wndmain.select_item(item) -- zaznaczenie podanego elelemntu '''
		self._photo_list.select_item(item)


	def __create_popup_menu(self, item):
		popup_menu = wx.Menu()

		def append(name, func):
			mid = wx.NewId()
			popup_menu.Append(mid, name)
			wx.EVT_MENU(self, mid, func)

		if isinstance(item, Directory):
			append(_('Properties'), self._on_dirtree_item_activate)

			if not item.catalog.readonly:
				popup_menu.AppendSeparator()
				if isinstance(item, Disk):
					append(_('&Update disk...'), self._on_catalog_update_disk)
					append(_('&Delete disk...'), self._on_catalog_del_disk)

				else:
					append(_('Delete selected &dir...'), self._on_catalog_del_dir)

			popup_menu.AppendSeparator()

		append(_('Close catalog'),	self._on_file_close)

		return popup_menu


	def __create_popup_menu_image(self):
		popup_menu = wx.Menu()

		def append(name, func):
			mid = wx.NewId()
			popup_menu.Append(mid, name)
			wx.EVT_MENU(self, mid, func)

		append(_('Properties'), self._on_photo_popoup_properties)

		catalog = self._photo_list.selected_item.catalog
		if not catalog.readonly:
			popup_menu.AppendSeparator()
			append(_('&Delete file...'), self._on_catalog_del_image)

		return popup_menu



	def __update_changed_tags(self, tags_provider, changed_tags):
		""" wndmain.__update_changed_tags(tags_provider, changed_tags) -- aktualizacja tagów w drzewie """
		if changed_tags is not None and len(changed_tags) > 0:
			for tag_item in (tags_provider[tag] for tag in changed_tags):
				if tag_item.tree_node is not None:
					self._dirs_tree.update_node_tag(tag_item)

			self._dirs_tree.update_node_tags(tags_provider)


	def __update_menus_toolbars(self):
		""" wndmain.__update_menus_toolbars() -- włączanie/wyłączanie pozycji menu/toolbar """
		catalog_loaded = not self.catalogs_not_loaded

		catalog_writable = False
		if catalog_loaded:
			selected_tree_item = self._dirs_tree.selected_item
			if selected_tree_item is None:
				catalog_writable = not self._catalogs[0].readonly if len(self._catalogs) == 1 else False

			else:
				catalog_writable = not selected_tree_item.catalog.readonly

		self.__menu_bar.EnableTop(2, catalog_loaded)

		mm_items = self._main_menu_file.GetMenuItems()
		mm_items[2].Enable(catalog_loaded and catalog_writable)
		mm_items[4].Enable(catalog_loaded)
		mm_items[6].Enable(catalog_loaded and catalog_writable)
		mm_items[8].Enable(len(self._current_show_images) > 0)
		mm_items[9].Enable(len(self._current_show_images) > 0 and epdf.EPDF_AVAILABLE)

		self.__toolbar.EnableTool(self.__tb_find,	 catalog_loaded)
		self.__toolbar.EnableTool(self.__tb_add_disk, catalog_loaded)
		self.__toolbar.EnableTool(self.__tb_save,	catalog_loaded and catalog_writable)

		if catalog_loaded:
			disk_selected = isinstance(selected_tree_item, Disk) if selected_tree_item is not None else False
			dir_selected = not disk_selected and selected_tree_item is not None and isinstance(selected_tree_item, Directory)

			file_selected = self._photo_list.selected_count > 0

			mm_items = self._main_menu_catalog.GetMenuItems()
			mm_items[0].Enable(catalog_writable)
			mm_items[1].Enable(disk_selected and catalog_writable)
			mm_items[2].Enable(disk_selected and catalog_writable)
			mm_items[4].Enable(dir_selected and catalog_writable)
			mm_items[5].Enable(file_selected and catalog_writable)
			mm_items[7].Enable(file_selected and catalog_writable)


	def __update_settings(self):
		""" wndmain.__update_settings() -- aktualizacja wszystkiego na podstawie ustawien """
		appconfig = AppConfig()
		self._photo_list.set_thumb_size(
				appconfig.get('settings', 'thumb_width', 200), appconfig.get('settings', 'thumb_height', 200)
		)

		show_captions = appconfig.get('settings', 'view_show_captions', True)
		self._photo_list.show_captions	= show_captions
		self._menu_view_show_captions.Check(show_captions)

		self._photo_list.thumbs_preload	= appconfig.get('settings', 'view_preload', True)
		self._photo_list.set_captions_font(dict(appconfig.get_items('settings') or []))
		self._photo_list.update()
		self._photo_list.Refresh()

		show_info = appconfig.get('settings', 'view_show_info', True)
		self._menu_view_show_info.Check(show_info)
		self._toggle_info_panel(show_info)
		image.clear_cache()


	def _toggle_info_panel(self, show=None):
		""" wndmain._toggle_info_panel([show]) -- przełączenie widoczności paneli informacyjnego

			@param show	- None=toggle, True-wymuszenie pokazania, False=wymuszenie ukrycia
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
				self._layout_splitter_h.SplitHorizontally(wind1, self._info_panel, self._info_panel_size)

				# odswierzenie danych w panelu
				self._on_thumb_sel_changed(None)
				item = self._dirs_tree.selected_item
				if item is not None and isinstance(item, Directory):
					self._info_panel.show_folder(item)


	def _show_dir(self, images):
		''' wndmain._show_dir(images) -- wyświetlenie zawartości katalogu lub listy

			@param images	- Directory|[FileImage]|(FileImage) do wyświetlania; None oznacza odswieżenie aktualnego katalogu
		'''
		force_sort = False

		if images:
			if self._menu_view_show_recur.IsChecked() and hasattr(images, 'images_recursive'):
				images = images.images_recursive
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

			cmp_func = self.__get_sort_function(False, force_sort)

			if images is None:
				# odświeżenie widoku
				self._photo_list.sort_current_dir(cmp_func)

			else:
				self._photo_list.show_dir(images, cmp_func)
				self._current_show_images = images

		else:
			self._photo_list.show_dir(images)
			self._current_show_images = images

		self.__update_menus_toolbars()


	def __update_tags_timeline(self, catalog):
		''' wndmain.__update_tags_timeline(catalog) -- odświerzenie dir tree: tags, timeline '''
		self._dirs_tree.update_node_tags(catalog.tags_provider, True)
		self._dirs_tree.update_timeline_node(catalog.timeline)


	def __info_panel_clear(self):
		''' wndmain.__info_panel_clear() -- wyczyszczenie info-panelu '''
		if self._info_panel is not None:
			self._info_panel.clear()


	def __get_sort_function(self, images_as_list, force=True):
		''' wndmain.__get_sort_function(images_as_list, [force]) -> func -- fukncja sortowania miniaturek

			@params images_as_list - (bool) czy funkcja dla listy obiektów FileImage (true) czy lista obketów Thumb (false)
			@params force - (bool) - wymuszenie sortowania listy (domyślnie nie sortowna dla nazw)

			@return (funkcja klucza, reverse)
		'''
		desc = self._menu_view_sort_desc.IsChecked()
		sort_by	= ecatalog.SORT_BY_DATE

		if self._menu_view_sort_name.IsChecked(): # sort by name
			if desc or images_as_list or force:
				sort_by = ecatalog.SORT_BY_NAME

			else:
				return None

		elif self._menu_view_group_path.IsChecked():
			sort_by = ecatalog.SORT_BY_PATH

		return ecatalog.get_sorting_function(sort_by, desc, images_as_list)





# vim: encoding=utf8:
