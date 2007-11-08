#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
MainWnd

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
import wx.lib.dialogs as dialogs

from kpylibs				import dialogs 
from kpylibs.appconfig		import AppConfig
from kpylibs.iconprovider	import IconProvider
from kpylibs.guitools		import create_menu, create_toolbar_button
from kpylibs.wnd_shell		import WndShell

from pc.model.catalog		import Catalog
from pc.model.folder		import Folder
from pc.model.disc			import Disc
from pc.model.image			import Image

from components.dirstree	import DirsTree
from components.imagelistctrl	import MyThumbnailCtrl, EVT_THUMBNAILS_SEL_CHANGED, EVT_THUMBNAILS_DCLICK
from components.infopanel	import InfoPanel

from _dlgabout				import DlgAbout
from _dlgadddisc			import DlgAddDisc
from _dlgproperties			import DlgProperties
from _dlgsearch				import DlgSearch



class WndMain(wx.Frame):
	""" MainWnd """

	def __init__(self, app, debug):
		_LOG.debug('MainWnd.__init__')
		wx.Frame.__init__(self, None, -1, "PC", size=(800, 600))

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
		splitter2.SetSashGravity(0.5)


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
			(_('&Add disc...'),	None,	_('Add disc to catalog'),	self._on_catalog_add,	None),
			(_('&Delete disc...'),	None,	_('Delete selected disc from catalog'),	self._on_catalog_del_disc,	None),
			('-'),
			(None,	'Ctrl+F',	_('Search in calalogs'),	self._on_catalog_search,	wx.ID_FIND,	 wx.ART_FIND),
			('-'),
			(_('&Edit selected files...'),	None,	'',	self._on_catalog_edit_multi,	None),
		))
		return menu


	def _create_main_menu_help(self):
		menu = create_menu(self, (
			(_('&About...'),	None,	_('About application'),	self._on_help_about,	wx.ID_ABOUT,	wx.ART_INFORMATION),
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
			self._app.ExitMainLoop()
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
			else:
				catalog = self._catalogs[0]
		else:
			if isinstance(tree_selected, Catalog):
				catalog = tree_selected
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
			else:
				tree_selected = self._catalogs[0]

		if isinstance(tree_selected, Catalog):
			catalog = tree_selected
		else:
			catalog = tree_selected.catalog

		try:
			self.SetCursor(wx.HOURGLASS_CURSOR)
			catalog.rebuild()
			dialogs.message_box_info(self, _('Rebuild catalog finished'), 'PC')
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
			tree_selected = self._catalogs[0]

		catalog = tree_selected.catalog

		dlg = DlgAddDisc(self)
		if dlg.ShowModal() == wx.ID_OK:
			allfiles = Catalog.fast_count_files_dirs(dlg.path)
			
			dlg_progress = wx.ProgressDialog(_("Adding disc"), "", maximum=allfiles,
					style=wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE)
		
			def update_progress(msg, cntr=[0]):
				cntr[0] = cntr[0] + 1
				dlg_progress.Update(cntr[0], msg)
			
			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				catalog.add_disc(dlg.path, dlg.name, dlg.descr, on_update=update_progress)
				catalog.save_catalog()
				self._dirs_tree.add_catalog(catalog)
			finally:
				self.SetCursor(wx.STANDARD_CURSOR)
				dlg_progress.Update(allfiles, _('Done!'))
				dlg_progress.Destroy()
		dlg.Destroy()


	def _on_catalog_del_disc(self, evt):
		if len(self._catalogs) == 0:
			return

		tree_selected = self._dirs_tree.selected_item
		if tree_selected is None or not isinstance(tree_selected, Disc):
			return

		if dialogs.message_box_warning_yesno(self, _('Delete disc %s?') % tree_selected.name, 'PC'):
			self._dirs_tree.delete_item(tree_selected)
			catalog = tree_selected.catalog
			catalog.del_disc(tree_selected)
			self._dirs_tree.update_catalog_node(catalog)


	def _on_catalog_search(self, evt):
		if len(self._catalogs) == 0:
			return
		
		dlg = DlgSearch(self, self._catalogs)
		dlg.Show()
		

	def _on_catalog_edit_multi(self, evt):
		folder = self._dirs_tree.selected_item
		if folder is None:
			return
		if isinstance(folder, Folder):
			pass
		elif isinstance(folder, Disc):
			folder = folder.root
		else:
			return

		if folder.files_count == 0:
			return

		image = Image(None, None, None, catalog=folder.catalog)

		dlg = DlgProperties(self, image)
		if dlg.ShowModal():
			selected_items = [ folder.files[idx] for idx in self._photo_list.selected_items ]
			Catalog.update_images_from_image(selected_items, image)
			folder.catalog.dirty = True
			self._dirs_tree.update_catalog_node(folder.catalog)
		dlg.Destroy()



	def _on_dirtree_item_select(self, evt):
		item = self._dirs_tree.selected_item
		self._info_panel.clear()
		self._info_panel.clear_folder()
		if isinstance(item, Folder):
			pass
		elif isinstance(item, Disc):
			item = item.root
		else:
			self._photo_list.ShowDir([])
			return

		if item is not None:
			self._photo_list.ShowDir(item)
			self._info_panel.show_folder(item)
			self.SetStatusText(_('Folders %d;  files: %d') % (item.subdirs_count, item.files_count))


	def _on_dirtree_item_activate(self, evt):
		item = self._dirs_tree.selected_item
		self._info_panel.clear()
		self._info_panel.clear_folder()
		if isinstance(item, Folder):
			pass
		elif isinstance(item, Disc):
			item = item.root
		else:
			return

		dlg = DlgProperties(self, item)
		if dlg.ShowModal():
			item.catalog.dirty = True
			self._info_panel.show_folder(item)
			self._dirs_tree.update_catalog_node(item.catalog)
		dlg.Destroy()


	def _on_thumb_sel_changed(self, evt):
		selected = self._photo_list.selected_item
		if selected is None:
			self._info_panel.clear()
		else:
			self._info_panel.show(selected)


	def _on_thumb_dclick(self, evt):
		selected = self._photo_list.selected_item
		if selected is not None:
			dlg = DlgProperties(self, selected)
			if dlg.ShowModal():
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
			try:
				self.SetCursor(wx.HOURGLASS_CURSOR)
				catalog = Catalog(filename)
				self._catalogs.append(catalog)
				self._dirs_tree.add_catalog(catalog)
				self.__update_last_open_files(filename)
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
