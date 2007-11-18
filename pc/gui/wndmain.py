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

import gettext
_ = gettext.gettext

import wx

from kpylibs				import dialogs
from kpylibs.appconfig		import AppConfig
from kpylibs.iconprovider	import IconProvider
from kpylibs.guitools		import create_menu, create_toolbar_button
from kpylibs.wnd_shell		import WndShell
from kpylibs.formaters		import format_size

import pc

from pc.model				import Catalog, Directory, Disk, Image, Tag

from components.dirstree	import DirsTree
from components.imagelistctrl	import MyThumbnailCtrl, EVT_THUMBNAILS_SEL_CHANGED, EVT_THUMBNAILS_DCLICK
from components.infopanel	import InfoPanel

from _dlgabout				import DlgAbout
from _dlgadddisk			import DlgAddDisk
from _dlgproperties			import DlgProperties
from _dlgsearch				import DlgSearch


_DEFAULT_ADD_OPTIONS = {
		'filter_folder_names': None,
		'include_empty': 0
}



class WndMain(wx.Frame):
	""" MainWnd """

	def __init__(self, app, debug):
		_LOG.debug('MainWnd.__init__')

		appconfig = AppConfig()
		size = (int(appconfig.get('main_wnd', 'size_x', 800)), int(appconfig.get('main_wnd', 'size_y', 600)))

		wx.Frame.__init__(self, None, -1, "PC %s" % pc.__version__, size=size)

		self._app			= app
		self._debug			= debug

		self._catalogs		= []
		self._layout_splitter	= None

		self._icon_provider = IconProvider()
		self._icon_provider.load_icons(['folder_image', 'add', 'delete', 'add_files', 'information',
			'folder1', 'folder_add', 'folder_edit', 'folder_delete', 'folder_go', 'disk'
		])

		self.SetIcon(self._icon_provider.get_icon('folder_image'))

		self.SetMenuBar(self._create_main_menu())
		self._create_toolbar()
		self._create_layout()
		self.CreateStatusBar(1, wx.ST_SIZEGRIP)

		self.Centre(wx.BOTH)

		wx.EVT_CLOSE(self, self._on_close)
		wx.EVT_SIZE(self, self._on_size)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_dirtree_item_select, self._dirs_tree)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_dirtree_item_activate, self._dirs_tree)
		self.Bind(EVT_THUMBNAILS_SEL_CHANGED, self._on_thumb_sel_changed)
		self.Bind(EVT_THUMBNAILS_DCLICK, self._on_thumb_dclick)
		self.Bind(wx.EVT_MENU_RANGE, self._on_file_history, id=wx.ID_FILE1, id2=wx.ID_FILE9)

		self.__update_last_open_files()


	def _create_layout(self):
		splitter = self._layout_splitter = wx.SplitterWindow(self, -1, style=wx.SP_NOBORDER|wx.SP_3DSASH) #|wx.SP_LIVE_UPDATE)

		splitter2 = wx.SplitterWindow(splitter, -1, style=wx.SP_NOBORDER|wx.SP_3DSASH)
		splitter2.SplitHorizontally(self._create_layout_photolist(splitter2), self._create_layout_info(splitter2), -150)

		splitter.SplitVertically(self._create_layout_tree(splitter), splitter2, 200)

		splitter.SetSashGravity(0.0)
		splitter2.SetSashGravity(1.0)


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
		toolbar.Realize()


	def _create_layout_tree(self, parent):
		self._dirs_tree = DirsTree(parent)
		return self._dirs_tree


	def _create_layout_photolist(self, parent):
		self._photo_list = MyThumbnailCtrl(parent)
		self._photo_list.ShowFileNames()
		return self._photo_list


	def _create_layout_info(self, parent):
		panel = self._info_panel = InfoPanel(parent)
		panel.event_add_listener('update_image', self._on_update_info_image)
		panel.event_add_listener('update_folder', self._on_update_info_folder)
		return panel


	#########################################################################################################


	def _on_close(self, evt):
		if dialogs.message_box_question_yesno(self, _('Close program?'), 'PC'):
			size_x, size_y = self.GetSizeTuple()

			appconfig = AppConfig()
			appconfig.set('main_wnd', 'size_x', size_x)
			appconfig.set('main_wnd', 'size_y', size_y)

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

		def save_catalog(catalog):
			self.SetCursor(wx.HOURGLASS_CURSOR)
			try:
				if catalog.dirty:
					catalog.save_catalog()
			except:
				_LOG.exception('WndMain._on_file_save(%s)' % catalog.name)
				dialogs.message_box_error(self, _('Error saving catalog %s') % filename, _('Save catalog'))
			self.SetCursor(wx.STANDARD_CURSOR)

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			for cat in self._catalogs:
				save_catalog(cat)
				self._dirs_tree.update_catalog_node(cat)
		else:
			save_catalog(tree_selected.catalog)
			self._dirs_tree.update_catalog_node(tree_selected.catalog)
		evt.Skip()


	def _on_file_close(self, evt):
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			if len(self._catalogs) > 1:
				return
			catalog = self._catalogs[0]
		else:
			catalog = tree_selected.catalog

		self._dirs_tree.delete_item(catalog)
		catalog.close()
		self._catalogs.remove(catalog)


	def _on_file_rebuild(self, evt):
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			if len(self._catalogs) > 1:
				return
			catalog = self._catalogs[0]
		else:
			catalog = tree_selected.catalog

		try:
			self.SetCursor(wx.HOURGLASS_CURSOR)
			saved_space = catalog.rebuild()
			dialogs.message_box_info(self, 
					_('Rebuild catalog finished\nSaved space: %sB') % format_size(saved_space, True, reduce_at=1024*1024, separate=True), 'PC')
		except:
			_LOG.exception('rebuild error')
		finally:
			self.SetCursor(wx.STANDARD_CURSOR)


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
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None:
			catalog = self._catalogs[0]
		else:
			catalog = tree_selected.catalog

		data = {}

		dlg = DlgAddDisk(self, data, catalog=catalog)
		if dlg.ShowModal() == wx.ID_OK:
			allfiles = Catalog.fast_count_files_dirs(data['path']) + 1

			dlg_progress = wx.ProgressDialog(_("Adding disk"), (" " * 70), parent=self, maximum=allfiles,
					style=wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME)

			def update_progress(msg, cntr=[0]):
				cntr[0] = cntr[0] + 1
				dlg_progress.Update(cntr[0], msg)

			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				catalog.add_disk(data['path'], data['name'], data['descr'], options=data, on_update=update_progress)
				catalog.save_catalog()
				self._dirs_tree.add_catalog(catalog)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)
				dlg_progress.Update(allfiles, _('Done!'))
				dlg_progress.Destroy()
		dlg.Destroy()


	def _on_catalog_update_disk(self, evt):
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Disk):
			return

		data = dict(name=tree_selected.name, descr=tree_selected.descr)

		dlg = DlgAddDisk(self, data, update=True, catalog=tree_selected.catalog)
		if dlg.ShowModal() == wx.ID_OK:
			catalog		= tree_selected.catalog
			allfiles	= Catalog.fast_count_files_dirs(data['path']) + 1

			dlg_progress = wx.ProgressDialog(_("Updating disk"), (" " * 70), parent=self, maximum=allfiles,
					style=wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME)

			def update_progress(msg, cntr=[0]):
				cntr[0] = cntr[0] + 1
				dlg_progress.Update(cntr[0], msg)

			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				catalog.update_disk(data['path'], tree_selected, options=data, on_update=update_progress, name=data['name'], descr=data['descr'])
				catalog.save_catalog()
				self._dirs_tree.add_catalog(catalog)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)
				dlg_progress.Update(allfiles, _('Done!'))
				dlg_progress.Destroy()
		dlg.Destroy()


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
			catalog.del_disk(tree_selected)
			self._dirs_tree.update_catalog_node(catalog)


	def _on_catalog_del_dir(self, evt):
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Directory):
			dialogs.message_box_error(self, _('No directory selected'), _('Delete directory'))
			return

		if dialogs.message_box_warning_yesno(self, _('Delete directory %s?') % tree_selected.name, 'PC'):
			self._dirs_tree.delete_item(tree_selected)
			tree_selected.parent.delete_subfolder(tree_selected)
			self._dirs_tree.update_catalog_node(tree_selected.catalog)
			self._dirs_tree.update_catalog_tags(tree_selected.catalog)


	def _on_catalog_del_image(self, evt):
		if len(self._catalogs) == 0:
			return

		folder = self._dirs_tree.selected_item
		if folder is None:
			return
		if isinstance(folder, Directory):
			pass
		elif isinstance(folder, Disk):
			folder = folder.root
		else:
			return

		if folder.files_count == 0:
			return

		selected_items = [ folder.files[idx] for idx in self._photo_list.selected_items ]
		if len(selected_items) == 0:
			return

		if dialogs.message_box_warning_yesno(self, _('Delete %d images?') % len(selected_items), 'PC'):
			for image in selected_items:
				folder.delete_image(image)
			self._photo_list.ShowDir(folder)
			self._info_panel.show_folder(folder)
			self._dirs_tree.update_catalog_node(folder.catalog)


	def _on_catalog_search(self, evt):
		if len(self._catalogs) == 0:
			return

		dlg = DlgSearch(self, self._catalogs)
		dlg.Show()


	def _on_catalog_edit_multi(self, evt):
		folder = self._dirs_tree.selected_item
		if folder is None:
			return
		if isinstance(folder, Directory):
			pass
		elif isinstance(folder, Disk):
			folder = folder.root
		else:
			return

		if folder.files_count == 0:
			return

		image = Image(None, None, None, catalog=folder.catalog)

		dlg = DlgProperties(self, image)
		if dlg.ShowModal() == wx.ID_OK:
			selected_items = [ folder.files[idx] for idx in self._photo_list.selected_items ]
			Catalog.update_images_from_image(selected_items, image)
			folder.catalog.dirty = True
			self._dirs_tree.update_catalog_node(folder.catalog)
		dlg.Destroy()


	def _on_dirtree_item_select(self, evt):
		item = self._dirs_tree.selected_item
		self._info_panel.clear()
		self._info_panel.clear_folder()
		show_info = True
		if isinstance(item, Directory):
			pass
		elif isinstance(item, Disk):
			item = item.root
		elif isinstance(item, Tag):
			item = tuple(( itm for itm in item.items if isinstance(itm, Image) ))
			show_info = False
		else:
			self._photo_list.ShowDir([])
			return

		if item is not None:
			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				self._photo_list.ShowDir(item)
				if show_info:
					self._info_panel.show_folder(item)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)
				if show_info:
					self.SetStatusText(_('Directorys %d;  files: %d') % (item.subdirs_count, item.files_count))
				else:
					self.SetStatusText(_('Files: %d') % len(item))



	def _on_dirtree_item_activate(self, evt):
		item = self._dirs_tree.selected_item
		self._info_panel.clear()
		self._info_panel.clear_folder()
		if isinstance(item, Directory):
			pass
		elif isinstance(item, Disk):
			item = item.root
		else:
			return

		dlg = DlgProperties(self, item)
		if dlg.ShowModal() == wx.ID_OK:
			item.catalog.dirty = True
			self._info_panel.show_folder(item)
			self._dirs_tree.update_catalog_node(item.catalog)
			self._dirs_tree.update_catalog_tags(item.catalog)
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
				self._on_update_info_image(selected)
			dlg.Destroy()


	def _on_file_history(self, evt):
		filehistnum = evt.GetId() - wx.ID_FILE1
		filename = AppConfig().last_open_files[filehistnum]
		self._open_file(filename)


	def _on_update_info_folder(self, folder):
		folder.catalog.dirty = True
		self._dirs_tree.update_catalog_node(folder.catalog)


	def _on_update_info_image(self, image):
		image.catalog.dirty = True
		self._dirs_tree.update_catalog_node(image.catalog)


	################################################################################


	def _open_file(self, filename):
		if sum(( 1 for cat in self._catalogs if cat.filename == filename )) == 0:
			if not os.path.exists(filename):
				dialogs.message_box_error(self, _("Error openning file %s!\nFile don't exists.") % filename, _('Open file'))
				return
			try:
				self.SetStatusText(_('Opening %s....  Please wait...') % filename)
				self.SetCursor(wx.HOURGLASS_CURSOR)
				catalog = Catalog(filename)
				self._catalogs.append(catalog)
				self._dirs_tree.add_catalog(catalog)
				self.__update_last_open_files(filename)
				self.SetStatusText(filename + ':  ' + ';  '.join(catalog.stat))
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


	def show_item(self, folder):
		self._dirs_tree.EnsureVisible(folder.tree_node)
		self._dirs_tree.SelectItem(folder.tree_node)



# vim: encoding=utf8:
