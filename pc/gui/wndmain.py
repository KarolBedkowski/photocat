#!/usr/bin/python2.4
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

from kpylibs				import dialogs
from kpylibs.appconfig		import AppConfig
from kpylibs.iconprovider	import IconProvider
from kpylibs.guitools		import create_menu, create_toolbar_button
from kpylibs.wnd_shell		import WndShell
from kpylibs.formaters		import format_size

import pc

from pc.model				import Catalog, Directory, Disk, FileImage, Tag, Timeline
from pc.model.storage		import Storage

from components.dirstree	import DirsTree
from components.imagelistctrl	import MyThumbnailCtrl, EVT_THUMBNAILS_SEL_CHANGED, EVT_THUMBNAILS_DCLICK
from components.infopanel	import InfoPanel
from components.thumbctrl	import ThumbCtrl

from _dlgabout				import DlgAbout
from _dlgadddisk			import DlgAddDisk
from _dlgproperties			import DlgProperties
from _dlgsearch				import DlgSearch
from _dlgsettings			import DlgSettings

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

		self._app			= app
		self._debug			= debug

		self._catalogs		= []
		self._layout_splitter	= None

		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['folder_image'])

		self.SetIcon(self._icon_provider.get_icon('folder_image'))

		self.SetMenuBar(self._create_main_menu())
		self._create_toolbar()
		self._create_layout(appconfig)
		self.CreateStatusBar(1, wx.ST_SIZEGRIP)

		position = appconfig.get('main_wnd', 'position')
		if position is None:
			self.Centre(wx.BOTH)
		else:
			self.Move(position)
	
		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Bind(wx.EVT_SIZE, self._on_size)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_dirtree_item_select, self._dirs_tree)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_dirtree_item_activate, self._dirs_tree)
		self.Bind(EVT_THUMBNAILS_SEL_CHANGED, self._on_thumb_sel_changed)
		self.Bind(EVT_THUMBNAILS_DCLICK, self._on_thumb_dclick)
		self.Bind(wx.EVT_MENU_RANGE, self._on_file_history, id=wx.ID_FILE1, id2=wx.ID_FILE9)
		self.Bind(wx.EVT_CONTEXT_MENU, self._on_dirtree_context_menu, self._dirs_tree)
		self._dirs_tree.Bind(wx.EVT_KEY_DOWN, self._on_dirtree_key_down)
		self._photo_list.bind_on_char(self._on_photolist_key_down)

		self.__update_last_open_files()


	def _create_layout(self, appconfig):
		splitter = self._layout_splitter_v = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER|wx.SP_3DSASH) #|wx.SP_LIVE_UPDATE)

		splitter2 = self._layout_splitter_h = wx.SplitterWindow(splitter, -1, style=wx.SP_NOBORDER|wx.SP_3DSASH)
		splitter2.SplitHorizontally(self._create_layout_photolist(splitter2), self._create_layout_info(splitter2))

		splitter.SplitVertically(self._create_layout_tree(splitter), splitter2)

		splitter.SetSashGravity(0.0)
		splitter2.SetSashGravity(1.0)

		splitter.SetSashPosition(appconfig.get('main_wnd', 'splitter_v', 200))
		splitter2.SetSashPosition(appconfig.get('main_wnd', 'splitter_h', -150))


	def _create_main_menu(self):
		menu_bar = wx.MenuBar()
		menu_bar.Append(self._create_main_menu_file(),		_('&File'))
		menu_bar.Append(self._create_main_menu_catalog(),	_('&Catalog'))
		menu_bar.Append(self._create_main_menu_help(),		wx.GetStockLabel(wx.ID_HELP, True))
		if self._debug:
			menu_bar.Append(self._create_main_menu_debug(),	'&Debug')
		return menu_bar


	def _create_main_menu_file(self):
		menu = create_menu(self, (
			(None,	'Ctrl-N',	_('Create new catalog'),	self._on_file_new,		wx.ID_NEW,		wx.ART_NEW),
			(None,	'Ctrl+O',	_('Load catalog'),			self._on_file_open,		wx.ID_OPEN,		wx.ART_FILE_OPEN),
			(None,	'Ctrl+S',	_('Save current catalog'),	self._on_file_save,		wx.ID_SAVE,		wx.ART_FILE_SAVE),
			(_('Close catalog'),	'Ctrl+Q',	_('Close current catalog'),	self._on_file_close),
			('-'),
			(_('Rebuild catalog'),	None,		_('Rebuild catalog'),		self._on_file_rebuild),
			('-'),
			(_('Program settings'),	None,		_('Program settings'),		self._on_file_settings),
			('-'),
			(None,	'Alt-F4',	_('Close application'),		self._on_close,			wx.ID_EXIT,		wx.ART_QUIT)
		))
		self._main_menu_file = menu

		self._main_menu_file_recent = wx.Menu()
		self._main_menu_file_recent_item = self._main_menu_file.InsertMenu(3, -1, _('Recent files'),
				self._main_menu_file_recent)

		return menu


	def _create_main_menu_catalog(self):
		menu = create_menu(self, (
			(_('&Add disk...'),		None,	_('Add disk to catalog'),				self._on_catalog_add,		None,		wx.ART_NEW_DIR),
			(_('&Update disk...'),	None,	_('Update selected disk'),				self._on_catalog_update_disk),
			(_('&Delete disk...'),	None,	_('Delete selected disk from catalog'),	self._on_catalog_del_disk,	None,		wx.ART_DELETE),
			('-'),
			(_('Delete selected &dir...'),	None,	'',								self._on_catalog_del_dir),
			(_('Delete selected &image...'),	None,	'',							self._on_catalog_del_image),
			('-'),
			(_('&Edit selected files...'),	None,	'',								self._on_catalog_edit_multi),
			('-'),
			(None,				'Ctrl+F',	_('Search in calalogs'),				self._on_catalog_search,	wx.ID_FIND,	wx.ART_FIND),
			(_('Info'),			None,		_('About selected calalog...'),			self._on_catalog_info),
		))
		return menu


	def _create_main_menu_help(self):
		menu = create_menu(self, (
			(_('&About...'),	None,	'',	self._on_help_about,	wx.ID_ABOUT,	wx.ART_INFORMATION),
		))
		return menu


	def _create_main_menu_debug(self):
		menu = create_menu(self, (
			('Shell', 'Ctrl+L', '', self._on_debug_shell, None),
		))
		return menu


	def _create_toolbar(self):
		''' Utworzenie toolbar-a '''
		toolbar = self.CreateToolBar(wx.TB_HORIZONTAL|wx.NO_BORDER|wx.TB_FLAT|wx.TB_TEXT)
		toolbar.SetToolBitmapSize((16, 16))

		def cbtn(label, function, iconname, description=''):
			return create_toolbar_button(toolbar, label, function, self._icon_provider.get_image(iconname),
					description=description)

		def cbtna(label, function, iconname, description=''):
			return create_toolbar_button(toolbar, label, function, imgid=iconname, description=description)

		cbtna(wx.ID_NEW,	self._on_file_new,	wx.ART_NEW,			_('Create new catalog'))
		cbtna(wx.ID_OPEN,	self._on_file_open,	wx.ART_FILE_OPEN,	_('Load catalog'))
		cbtna(wx.ID_SAVE,	self._on_file_save,	wx.ART_FILE_SAVE,	_('Save catalog'))

		toolbar.AddSeparator()

		cbtna(wx.ID_FIND,	self._on_catalog_search, wx.ART_FIND,	_('Search in calalogs'))
		
		toolbar.AddSeparator()

		cbtna(_('Add disk...'),	self._on_catalog_add,	wx.ART_NEW_DIR,	_('Add disk to catalog'))

		toolbar.AddSeparator()
		toolbar.Realize()


	def _create_layout_tree(self, parent):
		self._dirs_tree = DirsTree(parent)
		return self._dirs_tree


	def _create_layout_photolist(self, parent):
		self._photo_list = ThumbCtrl(parent)
		self._photo_list.SetPopupMenu(self.__create_popup_menu_image())

		appconfig = AppConfig()
		self._photo_list.SetThumbSize(
				appconfig.get('settings', 'thumb_width', 200), appconfig.get('settings', 'thumb_height', 200)
		)
		return self._photo_list


	def _create_layout_info(self, parent):
		panel = self._info_panel = InfoPanel(parent)
		return panel


	#########################################################################################################


	def _on_close(self, evt):
		dirty_catalogs = [ catalog for catalog in self._catalogs if catalog.dirty ]

		if len(dirty_catalogs) > 0:
			removed = []
			for catalog in dirty_catalogs:
				res = dialogs.message_box_warning_yesnocancel(self,
						_("Catalog %s isn't saved\nSave it?") % catalog.caption, 'PC')
				if res == wx.ID_CANCEL:
					return
				elif res == wx.ID_YES:
					self.__save_catalog(catalog)

		elif not dialogs.message_box_question_yesno(self, _('Close program?'), 'PC'):
			return 

		[ catalog.close() for catalog in self._catalogs ]

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
			filename = dialogs.dialog_file_save(self, _('Catalog file name'), '*.index')
			if filename is not None:
				if not filename.endswith('.index'):
					filename = filename + '.index'
				try:
					self.SetCursor(wx.HOURGLASS_CURSOR)
					catalog = Catalog(filename)
					catalog.data_provider.open(True)
					self._catalogs.append(catalog)
					self._dirs_tree.add_catalog(catalog)
				finally:
					self.SetCursor(wx.STANDARD_CURSOR)
					self.__update_last_open_files(filename)
		evt.Skip()


	def _on_file_open(self, evt):
		filename = dialogs.dialog_file_load(self, _('Open file'), '*.index')
		if filename is not None:
			if not filename.endswith('.index'):
				filename = filename + '.index'
			self._open_file(filename)
		evt.Skip()


	def _on_file_save(self, evt):
		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			for cat in self._catalogs:
				self.__save_catalog(cat)
				self._dirs_tree.update_catalog_node(cat)
		else:
			self.__save_catalog(tree_selected.catalog)
			self._dirs_tree.update_catalog_node(tree_selected.catalog)
		evt.Skip()


	def _on_file_close(self, evt):
		catalog = self.__get_selected_catalog()
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
		catalog.close()
		self._catalogs.remove(catalog)


	def _on_file_rebuild(self, evt):
		catalog = self.__get_selected_catalog()
		if catalog is None:
			return

		if not dialogs.message_box_question_yesno(self, _('Rebuild catalog %s?') % catalog.caption, 'PC'):
			return

		try:
			self.SetCursor(wx.HOURGLASS_CURSOR)
			saved_space = catalog.data_provider.rebuild(catalog)
			self.__save_catalog(catalog)
			dialogs.message_box_info(self,
					_('Rebuild catalog finished\nSaved space: %sB') %
							format_size(saved_space, True, reduce_at=1024*1024, separate=True),
					'PC')
		except Exception, err:
			_LOG.exception('rebuild error')
			dialogs.message_box_error(self,
					_('Rebuild catalog error!\n%(msg)s') % dict(msg=err.message),
					'PC')
		finally:
			self.SetCursor(wx.STANDARD_CURSOR)


	def _on_file_settings(self, evt):
		dlg = DlgSettings(self)
		res = dlg.ShowModal()
		dlg.Destroy()
		appconfig = AppConfig()
		if res == wx.ID_OK:
			self._photo_list.SetThumbSize(
					appconfig.get('settings', 'thumb_width'), appconfig.get('settings', 'thumb_height')
			)


	def _on_help_about(self, evt):
		dlg = DlgAbout(self)
		dlg.ShowModal()
		dlg.Destroy()
		evt.Skip()


	def _on_debug_shell(self, evt):
		WndShell(self, locals()).Show()


	def _on_file_history(self, evt):
		filehistnum = evt.GetId() - wx.ID_FILE1
		config = AppConfig()
		filename = config.last_open_files[filehistnum]
		self.open_album(filename)


	def _on_catalog_add(self, evt):
		catalog = self.__get_selected_catalog()
		if catalog is not None:
			self.__add_or_update_disk(catalog)


	def _on_catalog_update_disk(self, evt):
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			return

		disk = tree_selected.disk
		self.__add_or_update_disk(disk.catalog, disk, True)


	def _on_catalog_del_disk(self, evt):
		if len(self._catalogs) == 0:
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
			self._dirs_tree.update_node_tags(tree_selected.catalog.tags_provider, True)
			self._dirs_tree.update_timeline_node(tree_selected.catalog.timeline)


	def _on_catalog_del_dir(self, evt):
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			dialogs.message_box_error(self, _('No directory selected'), _('Delete directory'))
			return

		if dialogs.message_box_warning_yesno(self, _('Delete directory %s?') % tree_selected.name, 'PC'):
			self._dirs_tree.delete_item(tree_selected)
			tree_selected.parent.remove_subdir(tree_selected)
			self._dirs_tree.update_catalog_node(tree_selected.catalog)
			self._dirs_tree.update_node_tags(tree_selected.catalog.tags_provider, True)


	def _on_catalog_del_image(self, evt):
		if len(self._catalogs) == 0:
			return

		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Catalog):
			return

		selected_items = [ folder.files[idx] for idx in self._photo_list.selected_items ]
		if len(selected_items) == 0:
			return

		if dialogs.message_box_warning_yesno(self, _('Delete %d images?') % len(selected_items), 'PC'):
			for image in selected_items:
				folder.remove_file(image)
			self._photo_list.ShowDir(folder)
			self._info_panel.show_folder(folder)
			self._dirs_tree.update_catalog_node(folder.catalog)


	def _on_catalog_search(self, evt):
		if len(self._catalogs) == 0:
			return

		dlg = DlgSearch(self, self._catalogs)
		dlg.Show()


	def _on_catalog_info(self, evt):
		if len(self._catalogs) == 0:
			return

		catalog = self.__get_selected_catalog()

		files_count, subdirs_count = 0, 0
		for disk in catalog.disks:
			disk_files_count, disk_subdirs_count, disk_files_count2, disk_subdirs_count2 = disk.directory_size
			files_count		+= disk_files_count + disk_files_count2
			subdirs_count	+= disk_subdirs_count + disk_subdirs_count2

		data = dict(disks=len(catalog.disks), files=files_count, dirs=subdirs_count)
		info = _('Disks: %(disks)d\nDirs: %(dirs)d\nFiles: %(files)d') % data
		dialogs.message_box_info(self, info, 'PC')



	def _on_catalog_edit_multi(self, evt):
		folder = self._dirs_tree.selected_item
		if folder is None or isinstance(folder, Catalog):
			return

		if len(folder.files) == 0:
			return

		image = FileImage(None, None, None, folder.disk, catalog=folder.catalog)

		dlg = DlgProperties(self, image)
		if dlg.ShowModal() == wx.ID_OK:
			selected_items = [ folder.files[idx] for idx in self._photo_list.selected_items ]
			changed_tags = Catalog.update_images_from_image(selected_items, image)
			folder.catalog.dirty = True
			self._dirs_tree.update_catalog_node(folder.catalog)
			self.__update_changed_tags(folder.catalog.tags_provider, changed_tags)
		dlg.Destroy()


	def _on_dirtree_item_select(self, evt):
		item = self._dirs_tree.selected_item
		self._info_panel.clear()
		self._info_panel.clear_folder()
		show_info = True

		if isinstance(item, Tag):
			item = item.files
			show_info = False
		elif isinstance(item, Timeline):
			# wyświtelanie timeline
			if item.level == 0:
				# nie wyświetlamy wszystkiego
				self._photo_list.ShowDir([])
				return
			elif len(item.files) > 1000:
				# jeżeli ilość plików > 1000 - ostrzeżenie i pytania 
				if not dialogs.message_box_warning_yesno(self, _('Number of files exceed 1000!\nShow %d files?') % len(item.files), _('PC')):
					self._photo_list.ShowDir([])
					self.SetStatusText(_('Files: %d') % len(item.files))
					return
			item = item.files
			show_info = False
		elif not isinstance(item, Directory):
			self._photo_list.ShowDir([])
			return

		self._dirs_tree.Expand(self._dirs_tree.selected_node)

		if item is not None:
			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				self._photo_list.ShowDir(item)
				if show_info:
					self._info_panel.show_folder(item)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)
				if show_info:
					files_count, subdirs_count, dummy, dummy = item.directory_size
					self.SetStatusText(_('Directorys %d;  files: %d') % (subdirs_count, files_count))
				else:
					self.SetStatusText(_('Files: %d') % len(item))


	def _on_dirtree_item_activate(self, evt):
		item = self._dirs_tree.selected_item
		self._info_panel.clear()
		self._info_panel.clear_folder()
		if isinstance(item, Catalog):
			return
		
		#if isinstance(item, Timeline):
		#	self._dirs_tree.Toggle(item.tree_node)
		#	return

		dlg = DlgProperties(self, item)
		if dlg.ShowModal() == wx.ID_OK:
			item.catalog.dirty = True		
			self._info_panel.show_folder(item)

			if isinstance(item, Disk):
				self._dirs_tree.update_node_disk(item, False)
			else:
				self._dirs_tree.update_node_directory(item, False)

			self._dirs_tree.update_catalog_node(item.catalog)
			self.__update_changed_tags(item.catalog.tags_provider, dlg.changed_tags)
		dlg.Destroy()


	def _on_thumb_sel_changed(self, evt):
		selected = self._photo_list.selected_item
		if selected is None:
			self._info_panel.clear()
		else:
			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				self._info_panel.show(selected)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)


	def _on_thumb_dclick(self, evt):
		selected = self._photo_list.selected_item
		if selected is not None:
			dlg = DlgProperties(self, selected)
			if dlg.ShowModal() == wx.ID_OK:
				self._info_panel.show(selected)
				selected.catalog.dirty = True
				self._dirs_tree.update_catalog_node(selected.catalog)
				self.__update_changed_tags(selected.catalog.tags_provider, dlg.changed_tags)
			dlg.Destroy()


	def _on_file_history(self, evt):
		filehistnum = evt.GetId() - wx.ID_FILE1
		filename = AppConfig().last_open_files[filehistnum]
		self._open_file(filename)


	def _on_dirtree_context_menu(self, evt):
		item = self._dirs_tree.selected_item
		if item is None:
			return

		self.PopupMenu(self.__create_popup_menu(item))


	def _on_dirtree_key_down(self, evt):
		if len(self._catalogs) == 0:
			return

		if evt.GetKeyCode() == wx.WXK_DELETE:
			tree_selected = self._dirs_tree.selected_item
			if tree_selected is None:
				return
			if isinstance(tree_selected, Disk):
				self._on_catalog_del_disk(None)
			elif isinstance(tree_selected, Directory):
				self._on_catalog_del_dir(None)


	def _on_photolist_key_down(self, evt):
		if evt.m_keyCode == wx.WXK_DELETE:
			self._on_catalog_del_image(None)

	################################################################################


	def _open_file(self, filename):
		if sum(( 1 for cat in self._catalogs if cat.catalog_filename == filename )) == 0:
			if not os.path.exists(filename):
				dialogs.message_box_error(self, _("Error openning file %s!\nFile don't exists.") % filename, _('Open file'))
				return
			try:
				self.SetStatusText(_('Opening %s....  Please wait...') % filename)
				self.SetCursor(wx.HOURGLASS_CURSOR)
				catalog = Storage.load(filename)
				catalog.data_provider.open()
				self._catalogs.append(catalog)
				self._dirs_tree.add_catalog(catalog)
				self.__update_last_open_files(filename)
				self.SetStatusText(filename)
			except:
				_LOG.exception('WndMain._open_file(%s)' % filename)
				dialogs.message_box_error(self, _('Error openning file %s') % filename, _('Open file'))
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)


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
			for num in xrange(min(len(last_open_files), 10)):
				filename = os.path.basename(last_open_files[num])
				menu.Append(wx.ID_FILE1+num, "&%d. %s" % (num+1, filename), _('Open %s') % last_open_files[num])
			self._main_menu_file_recent_item.Enable(True)
		else:
			self._main_menu_file_recent_item.Enable(False)


	def __save_catalog(self, catalog, force=False):
		self.SetCursor(wx.HOURGLASS_CURSOR)
		if catalog.dirty or force:
			try:
				Storage.save(catalog)
			except:
				_LOG.exception('WndMain._on_file_save(%s)' % catalog.caption)
				dialogs.message_box_error(self, _('Error saving catalog %s') % catalog.catalog_filename, _('Save catalog'))
		self.SetCursor(wx.STANDARD_CURSOR)


	def show_item(self, folder):
		#self._dirs_tree.EnsureVisible(folder.tree_node)
		self._dirs_tree.show_node(folder)
		self._dirs_tree.SelectItem(folder.tree_node)


	def __create_popup_menu(self, item):
		popup_menu = wx.Menu()

		def append(name, func):
			mid = wx.NewId()
			popup_menu.Append(mid, name)
			wx.EVT_MENU(self, mid, func)

		if isinstance(item, Directory):
			append(_('Properties'), self._on_dirtree_item_activate)
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

		append(_('Properties'), self._on_thumb_dclick)
		popup_menu.AppendSeparator()
		append(_('&Delete file...'), self._on_catalog_del_image)

		return popup_menu


	def __add_or_update_disk(self, catalog, disk=None, update=False):
		if update:
			data = dict(name=disk.name, descr=disk.desc)
		else:
			data = {}
		appconfig = AppConfig()
		data.update(dict(appconfig.get_items('settings') or []))
		dlg = DlgAddDisk(self, data, update=update, catalog=catalog)
		if dlg.ShowModal() == wx.ID_OK:
			allfiles = Catalog.fast_count_files_dirs(data['path']) + 1
				
			title = update and _("Updating disk") or _("Adding disk")

			if allfiles == 1:
				dialogs.message_box_error(self, _('No files found!'), title)
				return

			dlg_progress = wx.ProgressDialog(title, ("  " * 30), parent=self, maximum=allfiles,
					style=wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_CAN_ABORT)

			def update_progress(msg, cntr=[0]):
				cntr[0] = cntr[0] + os.path.getsize(msg)
				return dlg_progress.Update(cntr[0], msg)

			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				if update:
					catalog.update_disk(disk, data['path'], descr=data['descr'], options=data, 
							on_update=update_progress, name=data['name'])
				else:
					disk = catalog.add_disk(data['path'], data['name'], data['descr'], options=data, on_update=update_progress)
				self.__save_catalog(catalog, True)
				#self._dirs_tree.add_catalog(catalog)
				self._dirs_tree.update_node_disk(disk)
				self._dirs_tree.update_node_tags(catalog.tags_provider, True)
				self._dirs_tree.update_timeline_node(catalog.timeline)
			except Exception, err:
				_LOG.exception('MainWnd.__add_or_update_disk()')
				self.SetCursor(wx.STANDARD_CURSOR)
				dialogs.message_box_error(self, _('Error:\n%s') % err, title)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)
				dlg_progress.Update(allfiles, _('Done!'))
				dlg_progress.Destroy()
		dlg.Destroy()


	def __get_selected_catalog(self):
		if len(self._catalogs) == 0:
			return None

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			if len(self._catalogs) > 1:
				return None
			catalog = self._catalogs[0]
		else:
			catalog = tree_selected.catalog
		return catalog


	def __update_changed_tags(self, tags_provider, changed_tags):
		""" aktualizacja tagów w drzewie """
		if changed_tags is not None and len(changed_tags) > 0:
			[ self._dirs_tree.update_node_tag(tag_item)
				for tag_item
				in (tags_provider[tag] for tag in changed_tags)
				if tag_item.tree_node is not None
			]
			self._dirs_tree.update_node_tags(tags_provider)


# vim: encoding=utf8:
