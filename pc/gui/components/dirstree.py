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

from pc.model import Tag, Image



class DirsTree(wx.TreeCtrl, EventGenerator):
	''' Drzewo katalogów '''

	def __init__(self, parent, wxid=-1):
		wx.TreeCtrl.__init__(self, parent, wxid,
				style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HIDE_ROOT)
		EventGenerator.__init__(self, ['change_selection'])

		self.__icon_provider = IconProvider()
		self.__icon_provider.load_icons(['folder', 'folder_open', 'folder_image', 'disk', 'tags', 'tag'])

		self.SetImageList(self.__icon_provider.get_image_list())
		self._icon_idx				= self.__icon_provider.get_image_index('folder')
		self._icon2_idx				= self.__icon_provider.get_image_index('folder_open')
		self._icon_folderimg_idx	= self.__icon_provider.get_image_index('folder_image')
		self._icon_disk_idx			= self.__icon_provider.get_image_index('disk')
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
			catalog_node = self.AppendItem(self._root, catalog.name, data=wx.TreeItemData(catalog))
			self.SetItemImage(catalog_node, self._icon_folderimg_idx, wx.TreeItemIcon_Normal)
			catalog.tree_node = catalog_node
		else:
			catalog_node = catalog.tree_node
			self.DeleteChildren(catalog_node)

		def add_dir(parent_node, dir):
			_LOG.debug('add_catalog add_dir %s' % dir.name)
			node = dir.tree_node = self.AppendItem(parent_node, dir.name, data=wx.TreeItemData(dir))
			self.SetItemImage(node, self._icon_idx, wx.TreeItemIcon_Normal)
			self.SetItemImage(node, self._icon2_idx, wx.TreeItemIcon_Expanded)

			[ add_dir(node, subdir) for subdir in dir.subdirs ]

		for disk in catalog.disks:
			_LOG.debug('add_catalog add_disk %s' % disk.name)
			disk.tree_node = disk_node = self.AppendItem(catalog_node, disk.name, data=wx.TreeItemData(disk))
			self.SetItemImage(disk_node, self._icon_disk_idx, wx.TreeItemIcon_Normal)

			[ add_dir(disk_node, subdir) for subdir in disk.root.subdirs ]

		node = catalog.tree_tags_node = self.AppendItem(catalog_node, _('Tags'), data=wx.TreeItemData(catalog.tags_provider))
		self.SetItemImage(node, self._icon_tags_idx, wx.TreeItemIcon_Normal)

		self.Expand(catalog_node)
		self.update_catalog_node(catalog)
		self.update_catalog_tags(catalog)


	def update_catalog_node(self, node):
		self.SetItemText(node.tree_node, node.caption)

	
	def update_node(self, node):
		self.SetItemText(node.tree_node, node.name)


	def delete_item(self, item):
		self.DeleteChildren(item.tree_node)
		self.Delete(item.tree_node)


	def update_catalog_tags(self, catalog):
		tags_node = catalog.tree_tags_node
		self.DeleteChildren(tags_node)

		for tag_name, tag in catalog.tags_provider.tags_items:
			tag.tree_node = self.AppendItem(tags_node, tag.caption, data=wx.TreeItemData(tag))
			self.SetItemImage(tag.tree_node, self._icon_tag_idx, wx.TreeItemIcon_Normal)
			if tag.size > 0:
				node = self.AppendItem(tag.tree_node, '...')


	def _on_expanding(self, evt):
		node = evt.GetItem()
		item = self.GetItemData(node).GetData()

		if not isinstance(item, Tag):
			return

		self.DeleteChildren(node)

		def add_dir(parent_node, dir):
			node = self.AppendItem(parent_node, dir.name, data=wx.TreeItemData(dir))
			self.SetItemImage(node, self._icon_idx, wx.TreeItemIcon_Normal)
			self.SetItemImage(node, self._icon2_idx, wx.TreeItemIcon_Expanded)

			[ add_dir(node, subdir) for subdir in dir.subdirs ]

		[ add_dir(node, item) for item in item.items if not isinstance(item, Image) ]



# vim: encoding=utf8: ff=unix:
