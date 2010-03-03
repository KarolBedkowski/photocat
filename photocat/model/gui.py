# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


class TreeItem(object):

	def __init__(self):
		self.tree_node = None

	def __del__(self):
		del self.tree_node

	@property
	def caption(self):
		return ''

	@property
	def childs(self):
		return None


# vim: encoding=utf8: ff=unix:
