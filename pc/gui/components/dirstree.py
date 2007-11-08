# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
 
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id: dirstree.py 2 2006-12-24 21:07:13Z k $'

__all__			= ['DirsTree']


import logging
_LOG = logging.getLogger(__name__)

import wx

from kpylibs.eventgenerator	import EventGenerator
from kpylibs.iconprovider	import IconProvider



class DirsTree(wx.TreeCtrl, EventGenerator):
	''' Drzewo katalogów '''

	def __init__(self, parent, wxid=-1):
		wx.TreeCtrl.__init__(self, parent, wxid, 
				style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_HIDE_ROOT)
		EventGenerator.__init__(self, ['change_selection'])

		self.__icon_provider = IconProvider()
		self.__icon_provider.load_icons(['folder', 'folder_open', 'folder_image', 'disk'])

		self.SetImageList(self.__icon_provider.get_image_list())
		self._icon_idx = self.__icon_provider.get_image_index('folder')
		self._icon2_idx = self.__icon_provider.get_image_index('folder_open')
		self._icon_folderimg_idx = self.__icon_provider.get_image_index('folder_image')
		self._icon_disc_idx = self.__icon_provider.get_image_index('disk')

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

		for disc in catalog.discs:
			_LOG.debug('add_catalog add_disc %s' % disc.name)
			disc.tree_node = disc_node = self.AppendItem(catalog_node, disc.name, data=wx.TreeItemData(disc))
			self.SetItemImage(disc_node, self._icon_disc_idx, wx.TreeItemIcon_Normal)
		
			[ add_dir(disc_node, subdir) for subdir in disc.root.subdirs ]
		
		self.Expand(catalog_node)
		self.update_catalog_node(catalog)


	def update_catalog_node(self, node):
		self.SetItemText(node.tree_node, node.caption)


	def delete_item(self, item):
		self.DeleteChildren(item.tree_node)
		self.Delete(item.tree_node)


# vim: encoding=utf8: ff=unix: 
