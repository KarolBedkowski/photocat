# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""

"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'

__all__			= ['DirsTree']


import logging
_LOG = logging.getLogger(__name__)

import wx

from kabes.wxtools.iconprovider	import IconProvider

from pc.model import Tag, FileImage, Catalog, Directory, Disk, Tags, Timeline

_ = wx.GetTranslation



class DirsTree(wx.TreeCtrl):
	''' Drzewo katalogów '''

	def __init__(self, parent, wxid=-1):
		wx.TreeCtrl.__init__(self, parent, wxid,
				style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HIDE_ROOT|wx.SUNKEN_BORDER)

		self.__icon_provider = IconProvider()
		self.__icon_provider.load_icons(['folder_image', 'tags', 'tag', 'calendar',
				'date', 'calendar_view_month', 'calendar_view_day', 'calendar_view_week',
				wx.ART_FOLDER, wx.ART_FOLDER_OPEN, wx.ART_CDROM])

		self.SetImageList(self.__icon_provider.get_image_list())
		self._icon_idx				= self.__icon_provider.get_image_index(wx.ART_FOLDER)
		self._icon2_idx				= self.__icon_provider.get_image_index(wx.ART_FOLDER_OPEN)
		self._icon_folderimg_idx	= self.__icon_provider.get_image_index('folder_image')
		self._icon_disk_idx			= self.__icon_provider.get_image_index(wx.ART_CDROM)
		self._icon_tags_idx			= self.__icon_provider.get_image_index('tags')
		self._icon_tag_idx			= self.__icon_provider.get_image_index('tag')
		self._icon_timeline_idx		= self.__icon_provider.get_image_index('date')
		self._icon_calendars_idxs = [
			self.__icon_provider.get_image_index('calendar_view_month'),
			self.__icon_provider.get_image_index('calendar_view_week'),
			self.__icon_provider.get_image_index('calendar_view_day'),
		]

		self._root = item_root = self.AddRoot('')
		self.SetItemImage(item_root, self._icon_idx, wx.TreeItemIcon_Normal)
		self.SetItemImage(item_root, self._icon2_idx, wx.TreeItemIcon_Expanded)

		self.Bind(wx.EVT_TREE_DELETE_ITEM, self._on_tree_delete_item)
		self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self._on_expanding)


	#########################################################################


	@property
	def selected_item(self):
		''' dirtree.selected_item -> Directory -- pobranie zaznaczonego elementu drzewa '''
		node = self.GetSelection()
		data = None
		if node.IsOk():
			item = self.GetItemData(node)
			if item is not None:
				data = item.GetData()

		return data


	@property
	def selected_node_parent(self):
		''' dirtree.selected_node_parent -> Directory -- pobranie parenta zaznaczonego elementu drzewa '''
		node = self.GetSelection()
		parent = None
		if node.IsOk():
			parent = self.GetItemParent(node)
			if parent is None or not parent.IsOk():
				parent = None

		return parent


	@property
	def selected_node(self):
		''' dirtree.selected_node -> TreeItem -- pobrane zaznaczeonego elementu '''
		node = self.GetSelection()
		return node if node.IsOk() else None


	#######################################################################


	def add_catalog(self, catalog):
		''' dirtree.add_catalog(catalog) -- dodanie katalogu do drzewa

			@param catalog	- katalog do dodania
		'''
		self.Freeze()
		self.update_node_catalog(catalog)
		self.Expand(catalog.tree_node)
		self.Thaw()


	def update_catalog_node(self, node):
		''' dirtree.update_catalog_node(node) -- odświerzenie etykiety elementu drzewa '''
		self.SetItemText(node.tree_node, node.caption)


	def delete_item(self, item):
		''' dirtree.delete_item(item) -- usunięcie elementu i gałęzi drzewa '''
		self.DeleteChildren(item.tree_node)
		self.Delete(item.tree_node)


	def show_node(self, node):
		''' dirtree.show_node(node) -- wymuszenie pokazania elementu '''
		self.EnsureVisible(node.tree_node)


	def update_node_catalog(self, catalog, recursive=True):
		''' dirtree.update_node_catalog(catalog, [recursive]) -- odświeżenie katalogu

			@param catalog 		- katalog do odświerzenia
			@param recursive	- czy odświerzać też gałąź (def=true)
		'''
		_LOG.debug('update_node_catalog %s' % catalog.name)
		self.Freeze()

		catalog_node = catalog.tree_node

		if catalog_node is None or not catalog_node.IsOk():
			catalog_node = catalog.tree_node = self.AppendItem(self._root, catalog.caption, data=wx.TreeItemData(catalog))
			self.SetItemImage(catalog_node, self._icon_folderimg_idx, wx.TreeItemIcon_Normal)

		else:
			self.SetItemText(catalog_node, catalog.caption)

		if recursive:
			self.DeleteChildren(catalog_node)
			self.update_node_tags(catalog.tags_provider)

		self.update_timeline_node(catalog.timeline)

		if recursive:
			for disk in catalog.childs:
				self.update_node_disk(disk)

		self.Thaw()


	def update_node_disk(self, disk, recursive=True):
		''' dirtree.update_node_disk(disk, recursive=True) -- odsiweżenie elementu drzewa - dysku

			@param disk 		- dysk do odświerzenia
			@param recursive	- czy odświerzać też gałąź (def=true)
		'''
		_LOG.debug('update_node_disk %s'  % disk.name)
		disk_node = disk.tree_node

		if disk_node is None or not disk_node.IsOk():
			disk_node = disk.tree_node = self.AppendItem(disk.catalog.tree_node, disk.caption, data=wx.TreeItemData(disk))
			self.SetItemImage(disk_node, self._icon_disk_idx, wx.TreeItemIcon_Normal)

		else:
			self.SetItemText(disk_node, disk.caption)

		if recursive:
			self.DeleteChildren(disk_node)
			for dir in disk.childs:
				self.update_node_directory(dir)


	def update_node_directory(self, directory, recursive=True):
		''' dirtree.update_node_directory(dir, recursive=True) -- odsiweżenie elementu drzewa - folderu

			@param directory	- folder do odświerzenia
			@param recursive	- czy odświerzać też gałąź (def=true)
		'''
		_LOG.debug('update_node_directory %s'  %directory.name)
		dir_node = directory.tree_node

		if dir_node is None or not dir_node.IsOk():
			dir_node = directory.tree_node = self.AppendItem(
					directory.parent.tree_node, directory.caption, data=wx.TreeItemData(directory))
			self.SetItemImage(dir_node, self._icon_idx, wx.TreeItemIcon_Normal)
			self.SetItemImage(dir_node, self._icon2_idx, wx.TreeItemIcon_Expanded)

		elif dir_node.IsOk():
			self.SetItemText(dir_node, directory.caption)

		else:
			dir.tree_node = None
			return

		if recursive:
			self.DeleteChildren(dir_node)
			for subdir in directory.childs:
				self.update_node_directory(subdir)


	def update_node_tags(self, tags, clear=False):
		''' dirtree.update_node_tags(tags, recursive=True) -- odsiweżenie gałęzi tagów

			@param tags			- element tag do odświerzenia
			@param recursive	- czy odświerzać też gałąź (def=true)
		'''
		node = tags.tree_node

		if node is None or not node.IsOk():
			node = tags.tree_node = self.AppendItem(tags.catalog.tree_node, _('Tags'),
					data=wx.TreeItemData(tags.catalog.tags_provider))
			self.SetItemImage(node, self._icon_tags_idx, wx.TreeItemIcon_Normal)

		elif clear:
			self.DeleteChildren(node)

		current_nodes = []
		for tag_name, tag in tags.tags_items:
			if tag.count > 0:
				if tag.tree_node is None or clear:
					tag.tree_node = tag_node = self.AppendItem(node, tag.caption, data=wx.TreeItemData(tag))
					self.SetItemImage(tag_node, self._icon_tags_idx, wx.TreeItemIcon_Normal)

				else:
					self.SetItemText(tag.tree_node, tag.caption)
					if tags.current_tags_nodes.count(tag.tree_node) > 0:
						tags.current_tags_nodes.remove(tag.tree_node)

				self.update_node_tag(tag)

			else:
				if tag.tree_node is not None:
					self.DeleteChildren(tag.tree_node)
					self.Delete(tag.tree_node)
					if tags.current_tags_nodes.count(tag.tree_node) > 0:
						tags.current_tags_nodes.remove(tag.tree_node)

					tag.tree_node = None

		for tree_node in tags.current_tags_nodes:
			self.DeleteChildren(tree_node)
			self.Delete(tree_node)

		tags.current_tags_nodes = current_nodes
		self.SortChildren(node)


	def update_node_tag(self, tag):
		''' dirtree.update_node_tag(tag, recursive=True) -- odsiweżenie pojedyńczego taga

			@param tag			- element tag do odświerzenia
			@param recursive	- czy odświerzać też gałąź (def=true)
		'''
		_LOG.debug('_update_node_tag %s' % tag)
		node = tag.tree_node

		self.DeleteChildren(node)

		if tag.count == 0:
			# jeżeli tag nie ma nic - usunięcie go
			if tag.tree_node.IsOk():
				self.Delete(node)

			tag.tree_node = None
			return

		def add_subdir(parent_node, item):
			node = self.AppendItem(parent_node, item.caption, data=wx.TreeItemData(item))
			if isinstance(item, Disk):
				self.SetItemImage(node, self._icon_disk_idx, wx.TreeItemIcon_Normal)

			else:
				self.SetItemImage(node, self._icon_idx, wx.TreeItemIcon_Normal)
				self.SetItemImage(node, self._icon2_idx, wx.TreeItemIcon_Expanded)

			for subdir in item.childs:
				add_subdir(node, subdir)

			self.SortChildren(node)

		for dir in tag.dirs:
			add_subdir(node, dir)
			self.SortChildren(node)

	#####################################################################

	def update_timeline_node(self, timeline):
		''' dirtree.update_timeline_node(timeline) -- odsiweżenie elementu lini czasu '''
		_LOG.debug('update_timeline_node cat= %s' % timeline.catalog.name)

		self.SetCursor(wx.HOURGLASS_CURSOR)

		node = timeline.tree_node
		if node is None or not node.IsOk():
			node = timeline.tree_node = self.AppendItem(timeline.catalog.tree_node, _('Timeline'),
					data=wx.TreeItemData(timeline))

			self.SetItemImage(node, self._icon_timeline_idx, wx.TreeItemIcon_Normal)

		else:
			self.CollapseAndReset(node)

		timeline.load()

		def add_subdir(parent_node, item):
			node = self.AppendItem(parent_node, item.caption, data=wx.TreeItemData(item))
			item.tree_node = node
			self.SetItemImage(node, self._icon_calendars_idxs[item.level-1], wx.TreeItemIcon_Normal)

			[ add_subdir(node, subdir) for subdir in item.subdirs ]

		[ add_subdir(node, subdir) for subdir in timeline.subdirs ]

		self.SetCursor(wx.STANDARD_CURSOR)

	#####################################################################


	def _on_tree_delete_item(self, evt):
		''' dirtree._on_tree_delete_item(evt) -- callback na EVT_TREE_DELETE_ITEM.
			Usuwane elementy musza miec czyszczone tree_node - w wxgtk nie dziala dobrze IsOk
		'''
		node = evt.GetItem()
		if node.IsOk():
			item = self.GetItemData(node)
			if item is not None:
				data = item.GetData()
				if hasattr(data, 'tree_node') and data.tree_node == node:
					data.tree_node = None


	def _on_expanding(self, evt):
		''' dirtree._on_expanding(evt) -- callback na EVT_TREE_ITEM_EXPANDING. '''
		node = evt.GetItem()
		item = self.GetItemData(node).GetData()

		if isinstance(item, Timeline):
			if item.level == 0:
				self.update_timeline_node(item)



# vim: encoding=utf8: ff=unix:
