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
		self.update_node_catalog(catalog)
		self.Expand(catalog.tree_node)


	def update_catalog_node(self, node):
		self.SetItemText(node.tree_node, node.caption)

	
	def delete_item(self, item):
		self.DeleteChildren(item.tree_node)
		self.Delete(item.tree_node)


	def show_node(self, node):
		self.EnsureVisible(node.tree_node)
	

	def update_node_catalog(self, catalog, recursive=True):
		catalog_node = catalog.tree_node
		
		if catalog_node is None or not catalog_node.IsOk():
			catalog_node = catalog.tree_node = self.AppendItem(self._root, catalog.caption, data=wx.TreeItemData(catalog))
			self.SetItemImage(catalog_node, self._icon_folderimg_idx, wx.TreeItemIcon_Normal)
		else:
			self.SetItemText(catalog_node, catalog.caption)

		if recursive:
			self.DeleteChildren(catalog_node)

			self.update_node_tags(catalog.tags_provider)

			for disk in catalog.childs:
				_LOG.debug('_update_node_catalog add_disk %s' % disk.name)
				self.update_node_disk(disk)



	def update_node_disk(self, disk, recursive=True):
		disk_node = disk.tree_node
		
		if disk_node is None or not disk_node.IsOk():
			disk_node = disk.tree_node = self.AppendItem(disk.catalog.tree_node, disk.caption, data=wx.TreeItemData(disk))
			self.SetItemImage(disk_node, self._icon_disk_idx, wx.TreeItemIcon_Normal)
		else:
			self.SetItemText(disk_node, disk.caption)
			
		if recursive:
			self.DeleteChildren(disk_node)
			for dir in disk.childs:
				_LOG.debug('_update_node_disk add_dir %s' % dir.name)			
				self.update_node_directory(dir)


	def update_node_directory(self, dir, recursive=True):
		dir_node = dir.tree_node
		
		if dir_node is None or not dir_node.IsOk():
			dir_node = dir.tree_node = self.AppendItem(dir.parent.tree_node, dir.caption, data=wx.TreeItemData(dir))
			self.SetItemImage(dir_node, self._icon_idx, wx.TreeItemIcon_Normal)
			self.SetItemImage(dir_node, self._icon2_idx, wx.TreeItemIcon_Expanded)
		elif dir_node.IsOk():
			self.SetItemText(dir_node, dir.caption)
		else:
			dir.tree_node = None
			return

		if recursive:
			self.DeleteChildren(dir_node)
			for subdir in dir.childs:
				_LOG.debug('_update_node_directory add_dir %s' % dir.name)
				self.update_node_directory(subdir)


	def update_node_tags(self, tags, clear=False):
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
					_LOG.debug('_update_node_tags %s' % tag.name)
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


	def update_node_tag(self, tag):
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

		for dir in tag.dirs:
			add_subdir(node, dir)







# vim: encoding=utf8: ff=unix:
