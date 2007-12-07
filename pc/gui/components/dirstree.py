# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""

"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'

__all__			= ['DirsTree']


import gettext
_ = gettext.gettext

import logging
_LOG = logging.getLogger(__name__)

import wx

from kpylibs.eventgenerator	import EventGenerator
from kpylibs.iconprovider	import IconProvider

from pc.model import Tag, FileImage, Catalog, Directory, Disk, Tags



class DirsTree(wx.TreeCtrl, EventGenerator):
	''' Drzewo katalogów '''

	def __init__(self, parent, wxid=-1):
		wx.TreeCtrl.__init__(self, parent, wxid,
				style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HIDE_ROOT)
		EventGenerator.__init__(self, ['change_selection'])

		self.__icon_provider = IconProvider()
		self.__icon_provider.load_icons(['folder_image', 'tags', 'tag', 
			wx.ART_FOLDER, wx.ART_FOLDER_OPEN, wx.ART_CDROM])

		self.SetImageList(self.__icon_provider.get_image_list())
		self._icon_idx				= self.__icon_provider.get_image_index(wx.ART_FOLDER)
		self._icon2_idx				= self.__icon_provider.get_image_index(wx.ART_FOLDER_OPEN)
		self._icon_folderimg_idx	= self.__icon_provider.get_image_index('folder_image')
		self._icon_disk_idx			= self.__icon_provider.get_image_index(wx.ART_CDROM)
		self._icon_tags_idx			= self.__icon_provider.get_image_index('tags')
		self._icon_tag_idx			= self.__icon_provider.get_image_index('tag')

		item_root = self.AddRoot('')
		self.SetItemImage(item_root, self._icon_idx, wx.TreeItemIcon_Normal)
		self.SetItemImage(item_root, self._icon2_idx, wx.TreeItemIcon_Expanded)
		self._root = item_root

		wx.EVT_TREE_ITEM_EXPANDING(self, wxid, self._on_expanding)


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
			if not parent.IsOk():
				parent = None
		return parent


	@property
	def selected_node(self):
		''' dirtree.selected_node -> TreeItem -- pobrane zaznaczeonego elementu '''
		node = self.GetSelection()
		if not node.IsOk():
			node = None
		return node


	def get_item_by_xy(self, x, y):
		node, _flags = self.HitTest(wx.Point(x, y))
		data = None
		if node.IsOk():
			item = self.GetItemData(node)
			if item is not None:
				data = item.GetData()
		return data, node


	def add_catalog(self, catalog):
		if catalog.tree_node is None:
			catalog_node = self.AppendItem(self._root, catalog.caption, data=wx.TreeItemData(catalog))
			self.SetItemImage(catalog_node, self._icon_folderimg_idx, wx.TreeItemIcon_Normal)
			catalog.tree_node = catalog_node
		else:
			catalog_node = catalog.tree_node
			self.DeleteChildren(catalog_node)

		self._update_node_catalog(catalog_node, catalog)
		self.Expand(catalog_node)


	def update_catalog_node(self, node):
		self.SetItemText(node.tree_node, node.caption)

	
	def delete_item(self, item):
		self.DeleteChildren(item.tree_node)
		self.Delete(item.tree_node)


	def update_catalog_tags(self, catalog):
		return
		tags_node = catalog.tree_tags_node
		self.DeleteChildren(tags_node)

		for tag_name, tag in catalog.tags_provider.tags_items:
			tag.tree_node = self.AppendItem(tags_node, tag.caption, data=wx.TreeItemData(tag))
			self.SetItemImage(tag.tree_node, self._icon_tag_idx, wx.TreeItemIcon_Normal)
			if tag.size > 0:
				node = self.AppendItem(tag.tree_node, '...')


	def show_node(self, node):
		self.EnsureVisible(node.tree_node)


	def _on_expanding(self, evt):
		node = evt.GetItem()
		item = self.GetItemData(node).GetData()

		#self.update_node(node, item)
		if isinstance(item, Tag):
			self._update_node_tag(node, item)
		elif isinstance(item, Tags):
			self._update_node_tags(node, item)


	def update_node(self, node, item):
		self.DeleteChildren(node)
		self.SetItemText(node, item.caption)
		if isinstance(item, Catalog):
			self._update_node_catalog(node, item)
		elif isinstance(item, Disk):
			self._update_node_disk(node, item)
		elif isinstance(item, Directory):
			self._update_node_directory(node, item)


	def _update_node_catalog(self, node, catalog):
		catalog_node = node

		for disk in catalog.childs:
			_LOG.debug('_update_node_catalog add_disk %s' % disk.name)
			disk.tree_node = disk_node = self.AppendItem(catalog_node, disk.caption, data=wx.TreeItemData(disk))
			self.SetItemImage(disk_node, self._icon_disk_idx, wx.TreeItemIcon_Normal)
			self._update_node_disk(disk_node, disk)

		node = catalog.tree_tags_node = self.AppendItem(catalog_node, _('Tags'), data=wx.TreeItemData(catalog.tags_provider))
		self.SetItemImage(node, self._icon_tags_idx, wx.TreeItemIcon_Normal)
		self._update_node_tags(node, catalog.tags_provider)


	def _update_node_disk(self, node, disk):
		disk_node = node

		for dir in disk.childs:
			_LOG.debug('_update_node_disk add_dir %s' % dir.name)
			dir_node = dir.tree_node = self.AppendItem(disk_node, dir.caption, data=wx.TreeItemData(dir))
			self.SetItemImage(dir_node, self._icon_idx, wx.TreeItemIcon_Normal)
			self.SetItemImage(dir_node, self._icon2_idx, wx.TreeItemIcon_Expanded)
			self._update_node_directory(dir_node, dir)


	def _update_node_directory(self, node, dir):
		dir_node = node

		for subdir in dir.childs:
			_LOG.debug('_update_node_directory add_dir %s' % dir.name)
			subdir_node = subdir.tree_node = self.AppendItem(dir_node, subdir.caption, data=wx.TreeItemData(subdir))
			self.SetItemImage(subdir_node, self._icon_idx, wx.TreeItemIcon_Normal)
			self.SetItemImage(subdir_node, self._icon2_idx, wx.TreeItemIcon_Expanded)
			self._update_node_directory(subdir_node, subdir)


	def _update_node_tags(self, node, tags):
		self.DeleteChildren(node)
		for tag_name, tag in tags.tags_items:
			if tag.files_count + tag.dirs_count > 0:
				_LOG.debug('_update_node_tags %s' % tag.name)
				tag_node = self.AppendItem(node, tag.caption, data=wx.TreeItemData(tag))
				self.SetItemImage(tag_node, self._icon_tags_idx, wx.TreeItemIcon_Normal)
				if tag.dirs_count > 0:
					self.AppendItem(tag_node, '...')


	def _update_node_tag(self, node, tag):
		_LOG.debug('_update_node_tag %s' % tag.name)

		self.DeleteChildren(node)

		def add_subdir(parent_node, item):
			node = self.AppendItem(parent_node, item.caption, data=wx.TreeItemData(item))
			self.SetItemImage(node, self._icon_idx, wx.TreeItemIcon_Normal)
			self.SetItemImage(node, self._icon2_idx, wx.TreeItemIcon_Expanded)
			for subdir in item.childs:
				add_subdir(node, subdir)

		for dir in tag.dirs:
			add_subdir(node, dir)








# vim: encoding=utf8: ff=unix:
